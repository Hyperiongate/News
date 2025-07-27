"""
FILE: services/pdf_generator.py
LOCATION: news/services/pdf_generator.py
PURPOSE: Generate professional PDF reports for news analysis with comprehensive bias data
DEPENDENCIES: reportlab
"""

import io
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.graphics.shapes import Drawing, Circle, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.graphics import renderPDF

class PDFGenerator:
    """Generate professional PDF reports for news analysis"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=20,
            borderWidth=0,
            borderPadding=0,
            borderColor=colors.HexColor('#e5e7eb'),
            borderRadius=4
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#059669'),
            spaceAfter=8,
            spaceBefore=12
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#374151'),
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ))
        
        # Alert/Warning style
        self.styles.add(ParagraphStyle(
            name='Alert',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#991b1b'),
            backColor=colors.HexColor('#fee2e2'),
            borderWidth=1,
            borderColor=colors.HexColor('#f87171'),
            borderPadding=8,
            borderRadius=4,
            spaceAfter=12
        ))
        
        # Success style
        self.styles.add(ParagraphStyle(
            name='Success',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#14532d'),
            backColor=colors.HexColor('#f0fdf4'),
            borderWidth=1,
            borderColor=colors.HexColor('#10b981'),
            borderPadding=8,
            borderRadius=4,
            spaceAfter=12
        ))
        
        # Info style
        self.styles.add(ParagraphStyle(
            name='Info',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#1e40af'),
            backColor=colors.HexColor('#eff6ff'),
            borderWidth=1,
            borderColor=colors.HexColor('#60a5fa'),
            borderPadding=8,
            borderRadius=4,
            spaceAfter=12
        ))
    
    def generate_analysis_pdf(self, analysis_data):
        """Generate a complete PDF report from analysis data"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build story (content)
        story = []
        
        # Add cover page
        story.extend(self._create_cover_page(analysis_data))
        story.append(PageBreak())
        
        # Add executive summary
        story.extend(self._create_executive_summary(analysis_data))
        story.append(PageBreak())
        
        # Add comprehensive bias analysis section
        if analysis_data.get('bias_analysis'):
            story.extend(self._create_comprehensive_bias_section(analysis_data['bias_analysis']))
            story.append(PageBreak())
        
        # Add fact checking section
        if analysis_data.get('fact_checks'):
            story.extend(self._create_fact_check_section(analysis_data['fact_checks'], 
                                                       analysis_data.get('fact_check_summary')))
            story.append(PageBreak())
        
        # Add author analysis section
        if analysis_data.get('author_analysis'):
            story.extend(self._create_enhanced_author_section(analysis_data['author_analysis']))
            story.append(PageBreak())
        
        # Add other analysis sections
        story.extend(self._create_detailed_analysis(analysis_data))
        
        # Add footer
        story.extend(self._create_footer())
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        buffer.seek(0)
        
        return buffer
    
    def _create_cover_page(self, data):
        """Create the cover page with trust score visualization"""
        elements = []
        
        # Logo/Title
        elements.append(Paragraph("News Analysis Report", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Article info
        if data.get('article'):
            article = data['article']
            elements.append(Paragraph(article.get('title', 'Untitled Article'), self.styles['Subtitle']))
            
            # Metadata table
            metadata = []
            if article.get('author'):
                metadata.append(['Author:', article['author']])
            if article.get('domain'):
                metadata.append(['Source:', article['domain']])
            if article.get('publish_date'):
                metadata.append(['Published:', article['publish_date']])
            if article.get('url'):
                # Truncate long URLs
                url = article['url']
                if len(url) > 60:
                    url = url[:57] + '...'
                metadata.append(['URL:', url])
            metadata.append(['Analysis Date:', datetime.now().strftime('%B %d, %Y')])
            
            if metadata:
                t = Table(metadata, colWidths=[2*inch, 4*inch])
                t.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
                    ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                elements.append(Spacer(1, 0.3*inch))
                elements.append(t)
        
        # Trust Score Visualization
        elements.append(Spacer(1, 0.5*inch))
        trust_score = data.get('trust_score', 0)
        elements.append(self._create_trust_score_graphic(trust_score))
        
        # Key metrics summary
        elements.append(Spacer(1, 0.5*inch))
        metrics = []
        
        if data.get('bias_analysis'):
            bias = data['bias_analysis']
            metrics.append(['Political Bias:', bias.get('overall_bias', 'Unknown')])
            metrics.append(['Objectivity Score:', f"{bias.get('objectivity_score', 0)}%"])
            if bias.get('bias_confidence'):
                metrics.append(['Analysis Confidence:', f"{bias['bias_confidence']}%"])
        
        if data.get('clickbait_score') is not None:
            clickbait_level = 'Low' if data['clickbait_score'] < 30 else 'Medium' if data['clickbait_score'] < 60 else 'High'
            metrics.append(['Clickbait Level:', f"{clickbait_level} ({data['clickbait_score']}%)"])
        
        if data.get('fact_checks'):
            total_checks = len(data['fact_checks'])
            verified = sum(1 for fc in data['fact_checks'] if fc.get('verdict', '').lower() in ['true', 'verified'])
            metrics.append(['Fact Checks:', f"{verified}/{total_checks} verified"])
        
        if data.get('source_credibility'):
            metrics.append(['Source Credibility:', data['source_credibility'].get('rating', 'Unknown')])
        
        if metrics:
            t = Table(metrics, colWidths=[2.5*inch, 3.5*inch])
            t.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 12),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f4f6')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(t)
        
        return elements
    
    def _create_connection_section(self, connection_data):
        """Create connection analysis section"""
        elements = []
        
        elements.append(Paragraph("Connection Web Analysis", self.styles['SectionHeader']))
        
        # Coherence score
        if connection_data.get('coherence_score') is not None:
            elements.append(self._create_score_bar_graphic(connection_data['coherence_score'], 
                                                          'Article Coherence'))
            elements.append(Spacer(1, 0.2*inch))
        
        # Topic connections
        if connection_data.get('topic_connections'):
            elements.append(Paragraph("Topic Connections", self.styles['SubsectionHeader']))
            
            topics = []
            for topic in connection_data['topic_connections']:
                topics.append([
                    topic.get('topic', 'Unknown'),
                    f"{topic.get('strength', 0)}%",
                    ', '.join(topic.get('keywords', [])[:3])
                ])
            
            if topics:
                t = Table([['Topic', 'Strength', 'Key Terms']] + topics, 
                         colWidths=[1.5*inch, 1*inch, 3*inch])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.2*inch))
        
        # Geographic relevance
        if connection_data.get('geographic_relevance'):
            elements.append(Paragraph("Geographic Scope", self.styles['SubsectionHeader']))
            
            geo = connection_data['geographic_relevance']
            primary_scope = connection_data.get('primary_scope', 'general')
            
            geo_text = f"Primary scope: <b>{primary_scope.capitalize()}</b> | "
            geo_text += f"Local: {geo.get('local', 0)}%, "
            geo_text += f"National: {geo.get('national', 0)}%, "
            geo_text += f"International: {geo.get('international', 0)}%"
            
            elements.append(Paragraph(geo_text, self.styles['CustomBody']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Related entities
        if connection_data.get('entities'):
            elements.append(Paragraph("Key Entities Mentioned", self.styles['SubsectionHeader']))
            
            entities = connection_data['entities']
            if entities.get('people'):
                elements.append(Paragraph(f"<b>People:</b> {', '.join(entities['people'][:5])}", 
                                        self.styles['CustomBody']))
            if entities.get('organizations'):
                elements.append(Paragraph(f"<b>Organizations:</b> {', '.join(entities['organizations'][:5])}", 
                                        self.styles['CustomBody']))
            if entities.get('locations'):
                elements.append(Paragraph(f"<b>Locations:</b> {', '.join(entities['locations'][:5])}", 
                                        self.styles['CustomBody']))
        
        return elements
    
    def _create_comprehensive_bias_section(self, bias_data):
        """Create comprehensive bias analysis section with all enhanced data"""
        elements = []
        
        elements.append(Paragraph("Comprehensive Bias Analysis", self.styles['SectionHeader']))
        
        # Bias confidence score
        if bias_data.get('bias_confidence'):
            elements.append(Paragraph(f"<b>Analysis Confidence:</b> {bias_data['bias_confidence']}%", 
                                    self.styles['CustomBody']))
            elements.append(Paragraph(self._get_confidence_description(bias_data['bias_confidence']), 
                                    self.styles['Info']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Multi-dimensional bias analysis
        if bias_data.get('bias_dimensions'):
            elements.append(Paragraph("Multi-dimensional Bias Analysis", self.styles['SubsectionHeader']))
            dimensions = bias_data['bias_dimensions']
            
            # Create table for dimensions
            dim_data = [['Dimension', 'Score', 'Assessment', 'Confidence']]
            for dim_name, dim_info in dimensions.items():
                score = dim_info.get('score', 0)
                # Convert score to percentage for display
                score_pct = abs(score * 100)
                direction = 'Left' if score < 0 else 'Right' if score > 0 else 'Neutral'
                if dim_name in ['sensational', 'corporate']:
                    direction = dim_info.get('label', 'Unknown')
                
                dim_data.append([
                    self._format_dimension_name(dim_name),
                    f"{score_pct:.0f}% {direction}",
                    dim_info.get('label', 'Unknown'),
                    f"{dim_info.get('confidence', 0)}%"
                ])
            
            t = Table(dim_data, colWidths=[1.5*inch, 1.5*inch, 2*inch, 1*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.2*inch))
        
        # Political lean visualization
        lean = bias_data.get('political_lean', 0)
        elements.append(Paragraph("Political Spectrum Analysis", self.styles['SubsectionHeader']))
        elements.append(self._create_political_spectrum_graphic(lean))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(self._get_political_description(lean), self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Bias patterns detected
        if bias_data.get('bias_patterns'):
            elements.append(Paragraph("Bias Patterns Detected", self.styles['SubsectionHeader']))
            
            for pattern in bias_data['bias_patterns']:
                severity_color = {
                    'high': colors.HexColor('#ef4444'),
                    'medium': colors.HexColor('#f59e0b'),
                    'low': colors.HexColor('#3b82f6')
                }.get(pattern.get('severity', 'medium'), colors.HexColor('#6b7280'))
                
                pattern_text = f"<b>{self._format_pattern_type(pattern['type'])}</b> " \
                              f"<font color='{severity_color}'>({pattern.get('severity', 'medium').upper()})</font>: " \
                              f"{pattern['description']}"
                elements.append(Paragraph(f"• {pattern_text}", self.styles['CustomBody']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Framing analysis
        if bias_data.get('framing_analysis') and bias_data['framing_analysis'].get('frames_detected', 0) > 0:
            elements.append(Paragraph("Framing Analysis", self.styles['SubsectionHeader']))
            framing = bias_data['framing_analysis']
            
            elements.append(Paragraph(f"<b>Frames Detected:</b> {framing['frames_detected']} " 
                                    f"({framing.get('framing_bias_level', 'moderate')} bias level)", 
                                    self.styles['CustomBody']))
            
            if framing.get('framing_patterns'):
                for frame_type, frame_data in framing['framing_patterns'].items():
                    if frame_data.get('detected'):
                        elements.append(Paragraph(f"<b>{self._format_frame_type(frame_type)}:</b>", 
                                                self.styles['CustomBody']))
                        if frame_data.get('examples'):
                            for example in frame_data['examples'][:2]:  # Limit to 2 examples
                                elements.append(Paragraph(f'    "{example}"', 
                                                        ParagraphStyle(
                                                            name='Example',
                                                            parent=self.styles['CustomBody'],
                                                            leftIndent=20,
                                                            fontName='Helvetica-Oblique',
                                                            fontSize=10
                                                        )))
            elements.append(Spacer(1, 0.2*inch))
        
        # Bias impact assessment
        if bias_data.get('bias_impact'):
            impact = bias_data['bias_impact']
            elements.append(Paragraph("Bias Impact Assessment", self.styles['SubsectionHeader']))
            
            severity = impact.get('severity', 'unknown')
            severity_style = {
                'high': self.styles['Alert'],
                'moderate': self.styles['CustomBody'],
                'low': self.styles['Success']
            }.get(severity, self.styles['CustomBody'])
            
            elements.append(Paragraph(f"<b>Impact Severity:</b> {severity.upper()}", severity_style))
            
            if impact.get('reader_impact'):
                elements.append(Paragraph("<b>Potential Reader Impact:</b>", self.styles['CustomBody']))
                for imp in impact['reader_impact']:
                    elements.append(Paragraph(f"• {imp}", self.styles['CustomBody']))
            
            if impact.get('factual_accuracy'):
                elements.append(Paragraph(f"<b>Factual Accuracy:</b> {impact['factual_accuracy']}", 
                                        self.styles['CustomBody']))
            
            if impact.get('recommendation'):
                elements.append(Paragraph(f"<b>Recommendation:</b> {impact['recommendation']}", 
                                        self.styles['Info']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Original bias metrics table
        metrics = [
            ['Metric', 'Value', 'Assessment'],
            ['Overall Bias', bias_data.get('overall_bias', 'Unknown'), 
             self._assess_overall_bias(bias_data.get('overall_bias'))],
            ['Objectivity Score', f"{bias_data.get('objectivity_score', 0)}%",
             'Good' if bias_data.get('objectivity_score', 0) > 70 else 'Fair' if bias_data.get('objectivity_score', 0) > 40 else 'Poor'],
            ['Opinion Content', f"{bias_data.get('opinion_percentage', 0)}%",
             'Low' if bias_data.get('opinion_percentage', 0) < 30 else 'Moderate' if bias_data.get('opinion_percentage', 0) < 60 else 'High'],
            ['Emotional Language', f"{bias_data.get('emotional_score', 0)}%",
             'Minimal' if bias_data.get('emotional_score', 0) < 30 else 'Some' if bias_data.get('emotional_score', 0) < 60 else 'Excessive']
        ]
        
        t = Table(metrics, colWidths=[2*inch, 1.5*inch, 2*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.2*inch))
        
        # Source bias analysis
        if bias_data.get('source_bias_analysis'):
            source_bias = bias_data['source_bias_analysis']
            elements.append(Paragraph("Source Selection Analysis", self.styles['SubsectionHeader']))
            
            elements.append(Paragraph(f"<b>Total Sources:</b> {source_bias.get('total_sources', 0)}", 
                                    self.styles['CustomBody']))
            elements.append(Paragraph(f"<b>Source Diversity Score:</b> {source_bias.get('diversity_score', 0)}%", 
                                    self.styles['CustomBody']))
            
            if source_bias.get('source_types'):
                source_data = []
                for s_type, count in source_bias['source_types'].items():
                    if count > 0:
                        source_data.append([self._format_source_type(s_type), str(count)])
                
                if source_data:
                    st = Table([['Source Type', 'Count']] + source_data, colWidths=[3*inch, 1*inch])
                    st.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6b7280')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    elements.append(st)
            elements.append(Spacer(1, 0.2*inch))
        
        # Manipulation tactics
        if bias_data.get('manipulation_tactics'):
            elements.append(Paragraph("Manipulation Tactics Detected", self.styles['SubsectionHeader']))
            
            for tactic in bias_data['manipulation_tactics']:
                if isinstance(tactic, dict):
                    text = f"<b>{tactic.get('name', 'Unknown')}</b>: {tactic.get('description', '')}"
                    severity = tactic.get('severity', 'medium')
                    if severity == 'high':
                        style = self.styles['Alert']
                    elif severity == 'low':
                        style = self.styles['Info']
                    else:
                        style = self.styles['CustomBody']
                else:
                    text = str(tactic)
                    style = self.styles['CustomBody']
                elements.append(Paragraph(f"• {text}", style))
            elements.append(Spacer(1, 0.2*inch))
        
        # Loaded phrases
        if bias_data.get('loaded_phrases'):
            elements.append(Paragraph("Loaded Language Examples", self.styles['SubsectionHeader']))
            
            # Limit to first 5 phrases for space
            for phrase in bias_data['loaded_phrases'][:5]:
                if isinstance(phrase, dict):
                    phrase_text = f'<b>"{phrase.get("text", "")}"</b>'
                    if phrase.get('type'):
                        phrase_text += f' <i>({phrase["type"]})</i>'
                    if phrase.get('explanation'):
                        phrase_text += f' - {phrase["explanation"]}'
                else:
                    phrase_text = f'"{phrase}"'
                elements.append(Paragraph(f"• {phrase_text}", self.styles['CustomBody']))
            
            if len(bias_data['loaded_phrases']) > 5:
                elements.append(Paragraph(f"<i>... and {len(bias_data['loaded_phrases']) - 5} more loaded phrases</i>", 
                                        self.styles['CustomBody']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Contributing factors
        if bias_data.get('bias_visualization', {}).get('contributing_factors'):
            elements.append(Paragraph("Main Contributing Factors to Bias", self.styles['SubsectionHeader']))
            
            factors = bias_data['bias_visualization']['contributing_factors']
            factor_data = [['Factor', 'Impact', 'Description']]
            
            for factor in factors:
                factor_data.append([
                    factor['factor'],
                    f"{int(factor['impact'] * 100)}%",
                    factor['description']
                ])
            
            ft = Table(factor_data, colWidths=[1.5*inch, 1*inch, 3.5*inch])
            ft.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('ALIGN', (0, 0), (1, -1), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef2f2')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(ft)
            elements.append(Spacer(1, 0.2*inch))
        
        # AI summary
        if bias_data.get('ai_summary'):
            elements.append(Paragraph("AI Analysis Summary", self.styles['SubsectionHeader']))
            elements.append(Paragraph(bias_data['ai_summary'], self.styles['Info']))
        
        return elements
    
    def _create_enhanced_author_section(self, author_data):
        """Create enhanced author analysis section with all data"""
        elements = []
        
        elements.append(Paragraph("Author Analysis", self.styles['SectionHeader']))
        
        # Author name and found status
        elements.append(Paragraph(f"<b>Author:</b> {author_data.get('name', 'Unknown')}", 
                                self.styles['CustomBody']))
        
        if not author_data.get('found'):
            elements.append(Paragraph("No detailed author information could be found.", 
                                    self.styles['Alert']))
            return elements
        
        # Credibility score visualization
        cred_score = author_data.get('credibility_score', 0)
        elements.append(Spacer(1, 0.1*inch))
        elements.append(self._create_score_bar_graphic(cred_score, 'Author Credibility'))
        elements.append(Spacer(1, 0.2*inch))
        
        # Biography
        if author_data.get('bio'):
            elements.append(Paragraph("<b>Biography:</b>", self.styles['SubsectionHeader']))
            elements.append(Paragraph(author_data['bio'], self.styles['CustomBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Verification status
        if author_data.get('verification_status'):
            ver = author_data['verification_status']
            elements.append(Paragraph("<b>Verification Status:</b>", self.styles['SubsectionHeader']))
            
            ver_data = []
            if ver.get('verified'):
                ver_data.append(['Platform Verified:', 'Yes'])
            if ver.get('journalist_verified'):
                ver_data.append(['Journalist Database:', 'Verified'])
            if ver.get('outlet_staff'):
                ver_data.append(['Staff Writer:', 'Yes'])
            
            if ver_data:
                vt = Table(ver_data, colWidths=[2*inch, 2*inch])
                vt.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
                    ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#10b981')),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                elements.append(vt)
                elements.append(Spacer(1, 0.1*inch))
        
        # Professional information
        if author_data.get('professional_info'):
            prof = author_data['professional_info']
            elements.append(Paragraph("<b>Professional Information:</b>", self.styles['SubsectionHeader']))
            
            prof_items = []
            if prof.get('current_position'):
                prof_items.append(f"• <b>Current Position:</b> {prof['current_position']}")
            if prof.get('years_experience'):
                prof_items.append(f"• <b>Experience:</b> {prof['years_experience']}+ years")
            if prof.get('outlets'):
                prof_items.append(f"• <b>Associated Outlets:</b> {', '.join(prof['outlets'][:5])}")
            if prof.get('expertise_areas'):
                prof_items.append(f"• <b>Expertise:</b> {', '.join(prof['expertise_areas'][:5])}")
            
            for item in prof_items:
                elements.append(Paragraph(item, self.styles['CustomBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Education
        if author_data.get('education'):
            elements.append(Paragraph("<b>Education:</b>", self.styles['SubsectionHeader']))
            for edu in author_data['education'][:3]:  # Limit to 3
                elements.append(Paragraph(f"• {edu}", self.styles['CustomBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Awards
        if author_data.get('awards'):
            elements.append(Paragraph("<b>Awards & Recognition:</b>", self.styles['SubsectionHeader']))
            for award in author_data['awards'][:3]:  # Limit to 3
                elements.append(Paragraph(f"• {award}", self.styles['CustomBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Metrics
        if author_data.get('metrics'):
            metrics = author_data['metrics']
            elements.append(Paragraph("<b>Author Metrics:</b>", self.styles['SubsectionHeader']))
            
            metric_data = []
            if metrics.get('article_count'):
                metric_data.append(['Total Articles:', str(metrics['article_count'])])
            if metrics.get('avg_credibility'):
                metric_data.append(['Average Credibility:', f"{metrics['avg_credibility']}%"])
            if metrics.get('transparency_score'):
                metric_data.append(['Transparency Score:', f"{metrics['transparency_score']}%"])
            
            if metric_data:
                mt = Table(metric_data, colWidths=[2*inch, 1.5*inch])
                mt.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                elements.append(mt)
                elements.append(Spacer(1, 0.1*inch))
        
        # Online presence
        if author_data.get('online_presence'):
            online = author_data['online_presence']
            if any(online.values()):
                elements.append(Paragraph("<b>Online Presence:</b>", self.styles['SubsectionHeader']))
                
                presence_items = []
                for platform, handle in online.items():
                    if handle:
                        presence_items.append(f"• <b>{platform.title()}:</b> {handle}")
                
                for item in presence_items[:5]:  # Limit to 5
                    elements.append(Paragraph(item, self.styles['CustomBody']))
                elements.append(Spacer(1, 0.1*inch))
        
        # Recent articles
        if author_data.get('recent_articles'):
            elements.append(Paragraph("<b>Recent Articles:</b>", self.styles['SubsectionHeader']))
            for article in author_data['recent_articles'][:3]:  # Limit to 3
                if isinstance(article, dict):
                    title = article.get('title', 'Untitled')
                    date = article.get('date', '')
                    elements.append(Paragraph(f"• {title} {f'({date})' if date else ''}", 
                                            self.styles['CustomBody']))
                else:
                    elements.append(Paragraph(f"• {article}", self.styles['CustomBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Credibility explanation
        if author_data.get('credibility_explanation'):
            exp = author_data['credibility_explanation']
            elements.append(Paragraph("<b>Credibility Assessment:</b>", self.styles['SubsectionHeader']))
            
            exp_style = self.styles['Success'] if cred_score >= 70 else \
                       self.styles['CustomBody'] if cred_score >= 40 else \
                       self.styles['Alert']
            
            elements.append(Paragraph(f"<b>{exp.get('level', 'Unknown')} Credibility:</b> {exp.get('explanation', '')}", 
                                    exp_style))
            
            if exp.get('advice'):
                elements.append(Paragraph(f"<b>Advice:</b> {exp['advice']}", self.styles['Info']))
        
        # Integrity information
        if author_data.get('journalistic_integrity'):
            integrity = author_data['journalistic_integrity']
            if integrity.get('corrections') or integrity.get('retractions'):
                elements.append(Paragraph("<b>Journalistic Integrity:</b>", self.styles['SubsectionHeader']))
                if integrity.get('corrections'):
                    elements.append(Paragraph(f"• Corrections issued: {integrity['corrections']}", 
                                            self.styles['CustomBody']))
                if integrity.get('retractions'):
                    elements.append(Paragraph(f"• Retractions: {integrity['retractions']}", 
                                            self.styles['Alert']))
        
        return elements
    
    def _create_fact_check_section(self, fact_checks, summary=None):
        """Create enhanced fact checking section"""
        elements = []
        
        elements.append(Paragraph("Fact Check Results", self.styles['SectionHeader']))
        
        # Summary
        if summary:
            elements.append(Paragraph(summary, self.styles['Info']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Statistics
        total = len(fact_checks)
        verified = sum(1 for fc in fact_checks if fc.get('verdict', '').lower() in ['true', 'verified'])
        false_claims = sum(1 for fc in fact_checks if fc.get('verdict', '').lower() in ['false', 'incorrect'])
        mixed = sum(1 for fc in fact_checks if 'partial' in fc.get('verdict', '').lower() or 'mixed' in fc.get('verdict', '').lower())
        unverified = total - verified - false_claims - mixed
        
        # Create statistics table
        stats_data = [
            ['Total Claims Checked:', str(total)],
            ['Verified as True:', f"{verified} ({int(verified/total*100) if total > 0 else 0}%)"],
            ['Found False:', f"{false_claims} ({int(false_claims/total*100) if total > 0 else 0}%)"],
            ['Partially True/Mixed:', f"{mixed} ({int(mixed/total*100) if total > 0 else 0}%)"],
            ['Unverified:', f"{unverified} ({int(unverified/total*100) if total > 0 else 0}%)"]
        ]
        
        st = Table(stats_data, colWidths=[2*inch, 2*inch])
        st.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(st)
        elements.append(Spacer(1, 0.3*inch))
        
        # Individual fact checks
        elements.append(Paragraph("Detailed Fact Checks", self.styles['SubsectionHeader']))
        
        # Group by importance if available
        high_importance = [fc for fc in fact_checks if fc.get('importance') == 'high']
        medium_importance = [fc for fc in fact_checks if fc.get('importance') == 'medium']
        low_importance = [fc for fc in fact_checks if fc.get('importance') == 'low']
        no_importance = [fc for fc in fact_checks if not fc.get('importance')]
        
        # Render high importance first
        if high_importance:
            elements.append(Paragraph("<b>High Importance Claims:</b>", self.styles['CustomBody']))
            for fc in high_importance:
                elements.extend(self._render_single_fact_check(fc))
        
        # Then medium
        if medium_importance:
            elements.append(Paragraph("<b>Medium Importance Claims:</b>", self.styles['CustomBody']))
            for fc in medium_importance:
                elements.extend(self._render_single_fact_check(fc))
        
        # Then low
        if low_importance:
            elements.append(Paragraph("<b>Low Importance Claims:</b>", self.styles['CustomBody']))
            for fc in low_importance:
                elements.extend(self._render_single_fact_check(fc))
        
        # Finally those without importance
        if no_importance:
            if high_importance or medium_importance or low_importance:
                elements.append(Paragraph("<b>Other Claims:</b>", self.styles['CustomBody']))
            for fc in no_importance:
                elements.extend(self._render_single_fact_check(fc))
        
        return elements
    
    def _render_single_fact_check(self, fc):
        """Render a single fact check"""
        elements = []
        
        # Claim text
        claim_text = fc.get('claim', fc.get('text', 'Unknown claim'))
        elements.append(Paragraph(f'<b>Claim:</b> "{claim_text}"', 
                                ParagraphStyle(
                                    name='Claim',
                                    parent=self.styles['CustomBody'],
                                    leftIndent=20,
                                    rightIndent=20,
                                    fontName='Helvetica-Oblique'
                                )))
        
        # Verdict with color
        verdict = fc.get('verdict', 'Unverified')
        verdict_color = colors.HexColor('#10b981') if verdict.lower() in ['true', 'verified'] else \
                       colors.HexColor('#ef4444') if verdict.lower() in ['false', 'incorrect'] else \
                       colors.HexColor('#f59e0b')
        
        # Confidence
        confidence = fc.get('confidence', 0)
        confidence_text = f" (Confidence: {confidence}%)" if confidence > 0 else ""
        
        elements.append(Paragraph(f"<b>Verdict:</b> <font color='{verdict_color}'>{verdict}</font>{confidence_text}", 
                                self.styles['CustomBody']))
        
        # Explanation
        if fc.get('explanation'):
            elements.append(Paragraph(f"<b>Explanation:</b> {fc['explanation']}", self.styles['CustomBody']))
        
        # Evidence
        if fc.get('evidence'):
            elements.append(Paragraph("<b>Evidence:</b>", self.styles['CustomBody']))
            for evidence in fc['evidence'][:3]:  # Limit to 3
                if isinstance(evidence, dict):
                    source = evidence.get('source', 'Unknown source')
                    text = evidence.get('text', '')
                    elements.append(Paragraph(f"    • {source}: {text}", self.styles['CustomBody']))
                else:
                    elements.append(Paragraph(f"    • {evidence}", self.styles['CustomBody']))
        
        # Methodology
        if fc.get('methodology'):
            elements.append(Paragraph(f"<b>Verification Method:</b> {fc['methodology']}", 
                                    ParagraphStyle(
                                        name='Method',
                                        parent=self.styles['CustomBody'],
                                        fontSize=9,
                                        textColor=colors.HexColor('#6b7280')
                                    )))
        
        elements.append(Spacer(1, 0.15*inch))
        return elements
    
    def _create_trust_score_graphic(self, score):
        """Create a visual representation of the trust score"""
        drawing = Drawing(400, 200)
        
        # Determine color based on score
        if score >= 70:
            color = colors.HexColor('#10b981')  # Green
            label = "High Trust"
        elif score >= 40:
            color = colors.HexColor('#f59e0b')  # Yellow
            label = "Moderate Trust"
        else:
            color = colors.HexColor('#ef4444')  # Red
            label = "Low Trust"
        
        # Create circular progress indicator
        # Background circle
        drawing.add(Circle(200, 100, 80, fillColor=colors.HexColor('#e5e7eb'), strokeColor=None))
        
        # Progress arc (simplified as a filled circle with percentage)
        # For simplicity, we'll use a pie chart
        pie = Pie()
        pie.x = 120
        pie.y = 20
        pie.width = 160
        pie.height = 160
        pie.data = [score, 100-score]
        pie.labels = [f'{score}%', '']
        pie.slices.strokeWidth = 0.5
        pie.slices[0].fillColor = color
        pie.slices[1].fillColor = colors.HexColor('#e5e7eb')
        pie.slices[0].labelRadius = 0.65
        pie.slices[1].labelRadius = 1.2
        pie.slices[0].fontName = 'Helvetica-Bold'
        pie.slices[0].fontSize = 24
        pie.slices[0].fillColor = color
        
        drawing.add(pie)
        
        # Add label
        drawing.add(String(200, 10, label, textAnchor='middle', fontSize=16, fillColor=color))
        
        return drawing
    
    def _create_executive_summary(self, data):
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Overall assessment
        if data.get('conversational_summary'):
            elements.append(Paragraph(data['conversational_summary'], self.styles['CustomBody']))
            elements.append(Spacer(1, 0.2*inch))
        elif data.get('article_summary'):
            elements.append(Paragraph(data['article_summary'], self.styles['CustomBody']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Key findings
        elements.append(Paragraph("Key Findings", self.styles['SubsectionHeader']))
        
        findings = []
        
        # Source credibility
        if data.get('source_credibility'):
            cred = data['source_credibility']
            findings.append(f"• Source Credibility: {cred.get('rating', 'Unknown')} - {cred.get('type', 'Unknown source type')}")
        
        # Bias analysis
        if data.get('bias_analysis'):
            bias = data['bias_analysis']
            findings.append(f"• Political Bias: {bias.get('overall_bias', 'Unknown')}")
            if bias.get('bias_confidence'):
                findings.append(f"• Bias Analysis Confidence: {bias['bias_confidence']}%")
            if bias.get('manipulation_tactics'):
                findings.append(f"• {len(bias['manipulation_tactics'])} manipulation tactics detected")
        
        # Author credibility
        if data.get('author_analysis'):
            author = data['author_analysis']
            if author.get('found'):
                findings.append(f"• Author Credibility: {author.get('credibility_score', 'Unknown')}/100")
            else:
                findings.append("• Author information not found")
        
        # Fact checking
        if data.get('fact_check_summary'):
            findings.append(f"• Fact Checking: {data['fact_check_summary']}")
        
        # Transparency
        if data.get('transparency_analysis'):
            trans = data['transparency_analysis']
            findings.append(f"• Transparency Score: {trans.get('transparency_score', 0)}%")
        
        # Clickbait
        if data.get('clickbait_score') is not None:
            findings.append(f"• Clickbait Score: {data['clickbait_score']}%")
        
        for finding in findings:
            elements.append(Paragraph(finding, self.styles['CustomBody']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        elements.append(Paragraph("Recommendations", self.styles['SubsectionHeader']))
        
        trust_score = data.get('trust_score', 0)
        if trust_score >= 70:
            rec_text = "This article appears to be from a credible source with good journalistic standards. The information presented can generally be trusted, though readers should always maintain critical thinking."
            elements.append(Paragraph(rec_text, self.styles['Success']))
        elif trust_score >= 40:
            rec_text = "This article has some credibility concerns. Verify key claims through additional sources and be aware of potential bias in the presentation."
            elements.append(Paragraph(rec_text, self.styles['CustomBody']))
        else:
            rec_text = "This article shows significant credibility issues. Exercise extreme caution and verify all claims through multiple independent sources before accepting the information as factual."
            elements.append(Paragraph(rec_text, self.styles['Alert']))
        
        # Additional recommendations based on specific issues
        if data.get('bias_analysis', {}).get('bias_impact', {}).get('recommendation'):
            elements.append(Paragraph(f"<b>Bias Consideration:</b> {data['bias_analysis']['bias_impact']['recommendation']}", 
                                    self.styles['Info']))
        
        return elements
    
    def _create_detailed_analysis(self, data):
        """Create other detailed analysis sections"""
        elements = []
        
        # Clickbait Analysis Section
        if data.get('clickbait_score') is not None:
            elements.extend(self._create_clickbait_section(data))
            elements.append(Spacer(1, 0.3*inch))
        
        # Transparency Analysis Section
        if data.get('transparency_analysis'):
            elements.extend(self._create_transparency_section(data['transparency_analysis']))
            elements.append(Spacer(1, 0.3*inch))
        
        # Content Depth Section
        if data.get('content_analysis'):
            elements.extend(self._create_content_section(data['content_analysis']))
            elements.append(Spacer(1, 0.3*inch))
        
        # Persuasion Analysis Section
        if data.get('persuasion_analysis'):
            elements.extend(self._create_persuasion_section(data['persuasion_analysis']))
            elements.append(Spacer(1, 0.3*inch))
        
        # Connection Analysis Section
        if data.get('connection_analysis'):
            elements.extend(self._create_connection_section(data['connection_analysis']))
        
        # Key Claims Section
        if data.get('key_claims') and not data.get('fact_checks'):
            elements.extend(self._create_key_claims_section(data['key_claims']))
        
        return elements
    
    def _create_key_claims_section(self, claims):
        """Create section for key claims when fact checking wasn't performed"""
        elements = []
        
        elements.append(Paragraph("Key Claims Identified", self.styles['SectionHeader']))
        elements.append(Paragraph("The following factual claims were identified but not verified:", 
                                self.styles['Info']))
        elements.append(Spacer(1, 0.1*inch))
        
        for i, claim in enumerate(claims, 1):
            claim_text = claim.get('text', 'Unknown claim')
            claim_type = claim.get('type', 'unknown')
            importance = claim.get('importance', 'medium')
            
            importance_color = {
                'high': colors.HexColor('#ef4444'),
                'medium': colors.HexColor('#f59e0b'),
                'low': colors.HexColor('#3b82f6')
            }.get(importance, colors.HexColor('#6b7280'))
            
            elements.append(Paragraph(
                f"{i}. <font color='{importance_color}'>[{importance.upper()}]</font> "
                f"<i>({claim_type})</i> {claim_text}",
                self.styles['CustomBody']
            ))
        
        return elements
    
    def _create_clickbait_section(self, data):
        """Create clickbait analysis section"""
        elements = []
        
        elements.append(Paragraph("Clickbait Analysis", self.styles['SectionHeader']))
        
        score = data.get('clickbait_score', 0)
        
        # Score visualization
        elements.append(self._create_score_bar_graphic(score, 'Clickbait Score'))
        elements.append(Spacer(1, 0.2*inch))
        
        # Assessment
        if score < 30:
            assessment = "The headline appears genuine and informative."
            style = self.styles['Success']
        elif score < 60:
            assessment = "The headline shows some sensational elements but is not overly misleading."
            style = self.styles['CustomBody']
        else:
            assessment = "The headline uses significant clickbait tactics that may mislead readers."
            style = self.styles['Alert']
        
        elements.append(Paragraph(assessment, style))
        
        # Clickbait indicators if available
        if data.get('clickbait_analysis', {}).get('indicators'):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("Clickbait Indicators Found:", self.styles['SubsectionHeader']))
            
            for indicator in data['clickbait_analysis']['indicators']:
                elements.append(Paragraph(f"• {indicator}", self.styles['CustomBody']))
        
        return elements
    
    def _create_transparency_section(self, trans_data):
        """Create transparency analysis section"""
        elements = []
        
        elements.append(Paragraph("Transparency & Sources", self.styles['SectionHeader']))
        
        # Transparency score
        score = trans_data.get('transparency_score', 0)
        elements.append(self._create_score_bar_graphic(score, 'Transparency Score'))
        elements.append(Spacer(1, 0.2*inch))
        
        # Key metrics
        if trans_data.get('named_source_ratio') is not None:
            elements.append(Paragraph(f"<b>Named Sources:</b> {trans_data['named_source_ratio']}%", 
                                    self.styles['CustomBody']))
        
        if trans_data.get('quote_ratio') is not None:
            elements.append(Paragraph(f"<b>Direct Quotes:</b> {trans_data['quote_ratio']}%", 
                                    self.styles['CustomBody']))
        
        if trans_data.get('total_sources') is not None:
            elements.append(Paragraph(f"<b>Total Sources Cited:</b> {trans_data['total_sources']}", 
                                    self.styles['CustomBody']))
        
        # Source types breakdown
        if trans_data.get('source_types'):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("Source Breakdown:", self.styles['SubsectionHeader']))
            
            source_data = []
            for source_type, count in trans_data['source_types'].items():
                if count > 0:
                    source_data.append([self._format_source_type(source_type), str(count)])
            
            if source_data:
                st = Table([['Source Type', 'Count']] + source_data, colWidths=[3*inch, 1*inch])
                st.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6b7280')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                elements.append(st)
        
        return elements
    
    def _create_content_section(self, content_data):
        """Create content analysis section"""
        elements = []
        
        elements.append(Paragraph("Content Depth Analysis", self.styles['SectionHeader']))
        
        # Basic metrics
        metrics = [
            ['Metric', 'Value'],
            ['Word Count', f"{content_data.get('word_count', 0)} words"],
            ['Reading Time', f"{content_data.get('reading_time', 0)} minutes"],
            ['Average Sentence Length', f"{content_data.get('average_sentence_length', 0)} words"],
            ['Paragraph Count', f"{content_data.get('paragraph_count', 0)}"],
            ['Complexity Score', f"{content_data.get('complexity_score', 0)}%"]
        ]
        
        t = Table(metrics, colWidths=[2.5*inch, 2.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3e8ff')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        
        # Content quality indicators
        if content_data.get('quality_indicators'):
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("Quality Indicators:", self.styles['SubsectionHeader']))
            
            quality = content_data['quality_indicators']
            if quality.get('has_quotes'):
                elements.append(Paragraph("✓ Contains direct quotes", self.styles['Success']))
            if quality.get('has_statistics'):
                elements.append(Paragraph("✓ Includes statistical data", self.styles['Success']))
            if quality.get('has_sources'):
                elements.append(Paragraph("✓ Cites sources", self.styles['Success']))
            if quality.get('has_expert_opinions'):
                elements.append(Paragraph("✓ Includes expert opinions", self.styles['Success']))
        
        return elements
    
    def _create_persuasion_section(self, persuasion_data):
        """Create persuasion analysis section"""
        elements = []
        
        elements.append(Paragraph("Persuasion Techniques", self.styles['SectionHeader']))
        
        # Persuasion score
        score = persuasion_data.get('persuasion_score', 0)
        elements.append(self._create_score_bar_graphic(score, 'Persuasion Intensity', 
                                                      reverse_colors=True))
        elements.append(Spacer(1, 0.2*inch))
        
        # Emotional appeals
        if persuasion_data.get('emotional_appeals'):
            elements.append(Paragraph("Emotional Appeals Detected", self.styles['SubsectionHeader']))
            
            appeals = persuasion_data['emotional_appeals']
            appeal_data = []
            
            for emotion, value in appeals.items():
                if value > 0:
                    appeal_data.append([emotion.capitalize(), f"{value}%"])
            
            if appeal_data:
                t = Table([['Emotion', 'Intensity']] + appeal_data, colWidths=[2*inch, 2*inch])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ec4899')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(t)
        
        # Logical fallacies
        if persuasion_data.get('logical_fallacies'):
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("Logical Fallacies Detected", self.styles['SubsectionHeader']))
            
            for fallacy in persuasion_data['logical_fallacies']:
                text = f"<b>{fallacy.get('type', 'Unknown')}</b>: {fallacy.get('description', '')}"
                elements.append(Paragraph(f"• {text}", self.styles['Alert']))
        
        # Persuasion techniques
        if persuasion_data.get('techniques'):
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("Persuasion Techniques Used", self.styles['SubsectionHeader']))
            
            for technique in persuasion_data['techniques']:
                elements.append(Paragraph(f"• {technique}", self.styles['CustomBody']))
        
        return elements
    
    def _create_connection_section(self, connection_data):
        """Create connection analysis section"""
        elements = []
        
        elements
