"""
FILE: services/pdf_generator.py
LOCATION: news/services/pdf_generator.py
PURPOSE: Generate professional PDF reports for news analysis
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
        
        # Add detailed analysis sections
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
        
        if data.get('clickbait_score') is not None:
            clickbait_level = 'Low' if data['clickbait_score'] < 30 else 'Medium' if data['clickbait_score'] < 60 else 'High'
            metrics.append(['Clickbait Level:', f"{clickbait_level} ({data['clickbait_score']}%)"])
        
        if data.get('fact_checks'):
            total_checks = len(data['fact_checks'])
            verified = sum(1 for fc in data['fact_checks'] if fc.get('verdict', '').lower() in ['true', 'verified'])
            metrics.append(['Fact Checks:', f"{verified}/{total_checks} verified"])
        
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
        
        # Key findings
        elements.append(Paragraph("Key Findings", self.styles['SubsectionHeader']))
        
        findings = []
        
        # Source credibility
        if data.get('analysis', {}).get('source_credibility'):
            cred = data['analysis']['source_credibility']
            findings.append(f"• Source Credibility: {cred.get('rating', 'Unknown')} - {cred.get('type', 'Unknown source type')}")
        
        # Bias analysis
        if data.get('bias_analysis'):
            bias = data['bias_analysis']
            findings.append(f"• Political Bias: {bias.get('overall_bias', 'Unknown')}")
            if bias.get('manipulation_tactics'):
                findings.append(f"• {len(bias['manipulation_tactics'])} manipulation tactics detected")
        
        # Author credibility
        if data.get('author_analysis'):
            author = data['author_analysis']
            findings.append(f"• Author Credibility: {author.get('credibility_score', 'Unknown')}/100")
        
        # Fact checking
        if data.get('fact_check_summary'):
            findings.append(f"• Fact Checking: {data['fact_check_summary']}")
        
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
        
        return elements
    
    def _create_detailed_analysis(self, data):
        """Create detailed analysis sections"""
        elements = []
        
        # Bias Analysis Section
        if data.get('bias_analysis'):
            elements.extend(self._create_bias_section(data['bias_analysis']))
            elements.append(Spacer(1, 0.3*inch))
        
        # Fact Checking Section
        if data.get('fact_checks'):
            elements.extend(self._create_fact_check_section(data['fact_checks']))
            elements.append(Spacer(1, 0.3*inch))
        
        # Clickbait Analysis Section
        if data.get('clickbait_score') is not None:
            elements.extend(self._create_clickbait_section(data))
            elements.append(Spacer(1, 0.3*inch))
        
        # Author Analysis Section
        if data.get('author_analysis'):
            elements.extend(self._create_author_section(data['author_analysis']))
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
        
        return elements
    
    def _create_bias_section(self, bias_data):
        """Create bias analysis section"""
        elements = []
        
        elements.append(Paragraph("Bias Analysis", self.styles['SectionHeader']))
        
        # Political lean visualization
        lean = bias_data.get('political_lean', 0)
        elements.append(self._create_political_spectrum_graphic(lean))
        elements.append(Spacer(1, 0.2*inch))
        
        # Bias metrics table
        metrics = [
            ['Metric', 'Value', 'Assessment'],
            ['Political Lean', f"{abs(lean)}% {'Left' if lean < 0 else 'Right' if lean > 0 else 'Center'}", 
             'Acceptable' if abs(lean) < 40 else 'Noticeable' if abs(lean) < 60 else 'Strong'],
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
        
        # Manipulation tactics
        if bias_data.get('manipulation_tactics'):
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("Manipulation Tactics Detected", self.styles['SubsectionHeader']))
            
            for tactic in bias_data['manipulation_tactics']:
                if isinstance(tactic, dict):
                    text = f"<b>{tactic.get('name', 'Unknown')}</b>: {tactic.get('description', '')}"
                else:
                    text = str(tactic)
                elements.append(Paragraph(f"• {text}", self.styles['CustomBody']))
        
        return elements
    
    def _create_political_spectrum_graphic(self, lean):
        """Create political spectrum visualization"""
        drawing = Drawing(400, 60)
        
        # Background gradient bar
        bar_width = 360
        bar_height = 30
        bar_x = 20
        bar_y = 15
        
        # Draw spectrum bar
        drawing.add(Rect(bar_x, bar_y, bar_width, bar_height, 
                        fillColor=colors.HexColor('#e5e7eb'), 
                        strokeColor=None))
        
        # Add colored sections
        colors_spectrum = [
            colors.HexColor('#3b82f6'),  # Left
            colors.HexColor('#e5e7eb'),  # Center
            colors.HexColor('#ef4444')   # Right
        ]
        
        # Draw gradient effect (simplified)
        section_width = bar_width / 3
        drawing.add(Rect(bar_x, bar_y, section_width, bar_height, 
                        fillColor=colors_spectrum[0], strokeColor=None))
        drawing.add(Rect(bar_x + section_width, bar_y, section_width, bar_height, 
                        fillColor=colors_spectrum[1], strokeColor=None))
        drawing.add(Rect(bar_x + 2*section_width, bar_y, section_width, bar_height, 
                        fillColor=colors_spectrum[2], strokeColor=None))
        
        # Add position marker
        position = bar_x + (bar_width / 2) + (lean / 100 * bar_width / 2)
        drawing.add(Circle(position, bar_y + bar_height/2, 8, 
                          fillColor=colors.HexColor('#1f2937'), 
                          strokeColor=colors.white,
                          strokeWidth=2))
        
        # Add labels
        drawing.add(String(bar_x, 5, 'Far Left', fontSize=9, textAnchor='start'))
        drawing.add(String(bar_x + bar_width/2, 5, 'Center', fontSize=9, textAnchor='middle'))
        drawing.add(String(bar_x + bar_width, 5, 'Far Right', fontSize=9, textAnchor='end'))
        
        return drawing
    
    def _create_fact_check_section(self, fact_checks):
        """Create fact checking section"""
        elements = []
        
        elements.append(Paragraph("Fact Check Results", self.styles['SectionHeader']))
        
        # Summary statistics
        total = len(fact_checks)
        verified = sum(1 for fc in fact_checks if fc.get('verdict', '').lower() in ['true', 'verified'])
        false_claims = sum(1 for fc in fact_checks if fc.get('verdict', '').lower() in ['false', 'incorrect'])
        
        summary_text = f"Analyzed {total} claims: {verified} verified as true, {false_claims} found false, {total - verified - false_claims} partially true or unverified."
        elements.append(Paragraph(summary_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Individual fact checks
        for i, fc in enumerate(fact_checks, 1):
            elements.append(Paragraph(f"Claim {i}:", self.styles['SubsectionHeader']))
            
            # Claim text
            claim_text = fc.get('claim', fc.get('text', 'Unknown claim'))
            elements.append(Paragraph(f'"{claim_text}"', ParagraphStyle(
                name='Claim',
                parent=self.styles['CustomBody'],
                leftIndent=20,
                rightIndent=20,
                fontName='Helvetica-Oblique'
            )))
            
            # Verdict
            verdict = fc.get('verdict', 'Unverified')
            verdict_color = colors.HexColor('#10b981') if verdict.lower() in ['true', 'verified'] else \
                           colors.HexColor('#ef4444') if verdict.lower() in ['false', 'incorrect'] else \
                           colors.HexColor('#f59e0b')
            
            elements.append(Paragraph(f"<b>Verdict:</b> <font color='{verdict_color}'>{verdict}</font>", 
                                    self.styles['CustomBody']))
            
            # Explanation
            if fc.get('explanation'):
                elements.append(Paragraph(f"<b>Explanation:</b> {fc['explanation']}", self.styles['CustomBody']))
            
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_clickbait_section(self, data):
        """Create clickbait analysis section"""
        elements = []
        
        elements.append(Paragraph("Clickbait Analysis", self.styles['SectionHeader']))
        
        score = data.get('clickbait_score', 0)
        
        # Score visualization
        elements.append(self._create_score_bar_graphic(score, 'Clickbait Score'))
        elements.append(Spacer(1, 0.2*inch))
        
        # Title analysis
        if data.get('title_analysis'):
            title_data = data['title_analysis']
            elements.append(Paragraph("Title Components Analysis", self.styles['SubsectionHeader']))
            
            components = [
                ['Component', 'Score', 'Assessment'],
                ['Sensationalism', f"{title_data.get('sensationalism', 0)}%",
                 'Low' if title_data.get('sensationalism', 0) < 30 else 'Medium' if title_data.get('sensationalism', 0) < 60 else 'High'],
                ['Curiosity Gap', f"{title_data.get('curiosity_gap', 0)}%",
                 'None' if title_data.get('curiosity_gap', 0) == 0 else 'Present'],
                ['Emotional Words', f"{title_data.get('emotional_words', 0)}%",
                 'Minimal' if title_data.get('emotional_words', 0) < 30 else 'Some' if title_data.get('emotional_words', 0) < 60 else 'Many']
            ]
            
            t = Table(components, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef3c7')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(t)
        
        # Indicators
        if data.get('clickbait_indicators'):
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("Clickbait Indicators Found", self.styles['SubsectionHeader']))
            
            for indicator in data['clickbait_indicators']:
                text = f"<b>{indicator.get('name', 'Unknown')}</b>: {indicator.get('description', '')}"
                elements.append(Paragraph(f"• {text}", self.styles['CustomBody']))
        
        return elements
    
    def _create_author_section(self, author_data):
        """Create author analysis section"""
        elements = []
        
        elements.append(Paragraph("Author Analysis", self.styles['SectionHeader']))
        
        # Author name and bio
        elements.append(Paragraph(f"<b>Author:</b> {author_data.get('name', 'Unknown')}", 
                                self.styles['CustomBody']))
        
        if author_data.get('bio'):
            elements.append(Paragraph(f"<b>Biography:</b> {author_data['bio']}", 
                                    self.styles['CustomBody']))
        
        # Credibility score
        cred_score = author_data.get('credibility_score', 0)
        elements.append(Spacer(1, 0.1*inch))
        elements.append(self._create_score_bar_graphic(cred_score, 'Author Credibility'))
        
        # Professional info
        if author_data.get('professional_info'):
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("Professional Information", self.styles['SubsectionHeader']))
            
            prof_info = author_data['professional_info']
            if prof_info.get('years_experience'):
                elements.append(Paragraph(f"• Experience: {prof_info['years_experience']}+ years", 
                                        self.styles['CustomBody']))
            if prof_info.get('outlets'):
                elements.append(Paragraph(f"• Associated outlets: {', '.join(prof_info['outlets'])}", 
                                        self.styles['CustomBody']))
        
        # Credibility explanation
        if author_data.get('credibility_explanation'):
            exp = author_data['credibility_explanation']
            elements.append(Spacer(1, 0.2*inch))
            
            exp_style = self.styles['Success'] if cred_score >= 70 else \
                       self.styles['CustomBody'] if cred_score >= 40 else \
                       self.styles['Alert']
            
            elements.append(Paragraph(f"<b>{exp.get('level', 'Unknown')} Credibility:</b> {exp.get('explanation', '')}", 
                                    exp_style))
        
        return elements
    
    def _create_transparency_section(self, trans_data):
        """Create transparency analysis section"""
        elements = []
        
        elements.append(Paragraph("Transparency & Sources", self.styles['SectionHeader']))
        
        # Transparency score
        score = trans_data.get('transparency_score', 0)
        elements.append(self._create_score_bar_graphic(score, 'Transparency Score'))
        elements.append(Spacer(1, 0.2*inch))
        
        # Source breakdown
        if trans_data.get('source_types'):
            elements.append(Paragraph("Source Breakdown", self.styles['SubsectionHeader']))
            
            source_types = trans_data['source_types']
            total_sources = sum(source_types.values())
            
            if total_sources > 0:
                # Create pie chart
                drawing = Drawing(300, 200)
                pie = Pie()
                pie.x = 50
                pie.y = 20
                pie.width = 200
                pie.height = 160
                
                data_values = []
                data_labels = []
                chart_colors = []
                color_map = {
                    'named_sources': colors.HexColor('#10b981'),
                    'anonymous_sources': colors.HexColor('#ef4444'),
                    'official_sources': colors.HexColor('#3b82f6'),
                    'expert_sources': colors.HexColor('#8b5cf6'),
                    'document_references': colors.HexColor('#f59e0b')
                }
                
                for source_type, count in source_types.items():
                    if count > 0:
                        data_values.append(count)
                        data_labels.append(f"{source_type.replace('_', ' ').title()}: {count}")
                        chart_colors.append(color_map.get(source_type, colors.grey))
                
                pie.data = data_values
                pie.labels = data_labels
                
                for i, color in enumerate(chart_colors):
                    pie.slices[i].fillColor = color
                
                drawing.add(pie)
                elements.append(drawing)
            
            # Metrics
            elements.append(Paragraph(f"Total sources cited: {total_sources}", self.styles['CustomBody']))
            elements.append(Paragraph(f"Named source ratio: {trans_data.get('named_source_ratio', 0)}%", 
                                    self.styles['CustomBody']))
            elements.append(Paragraph(f"Direct quotes: {trans_data.get('quote_ratio', 0)}%", 
                                    self.styles['CustomBody']))
        
        return elements
    
    def _create_content_section(self, content_data):
        """Create content analysis section"""
        elements = []
        
        elements.append(Paragraph("Content Depth Analysis", self.styles['SectionHeader']))
        
        # Basic metrics
        metrics = [
            ['Metric', 'Value'],
            ['Word Count', f"{content_data.get('word_count', 0)} words"],
            ['Reading Level', content_data.get('reading_level', 'Unknown')],
            ['Average Sentence Length', f"{content_data.get('avg_sentence_length', 0)} words"],
            ['Complexity', f"{content_data.get('complexity_ratio', 0)}% complex words"],
            ['Emotional Tone', content_data.get('emotional_tone', 'neutral').capitalize()]
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
        
        # Content composition
        if content_data.get('facts_vs_opinion'):
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("Content Composition", self.styles['SubsectionHeader']))
            
            fvo = content_data['facts_vs_opinion']
            total = fvo.get('facts', 0) + fvo.get('opinions', 0) + fvo.get('analysis', 0)
            
            if total > 0:
                comp_text = f"Facts: {fvo.get('facts', 0)} sentences, " \
                           f"Analysis: {fvo.get('analysis', 0)} sentences, " \
                           f"Opinions: {fvo.get('opinions', 0)} sentences"
                elements.append(Paragraph(comp_text, self.styles['CustomBody']))
        
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
        
        return elements
    
    def _create_connection_section(self, connection_data):
        """Create connection analysis section"""
        elements = []
        
        elements.append(Paragraph("Connection Web Analysis", self.styles['SectionHeader']))
        
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
        
        # Geographic relevance
        if connection_data.get('geographic_relevance'):
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("Geographic Scope", self.styles['SubsectionHeader']))
            
            geo = connection_data['geographic_relevance']
            primary_scope = connection_data.get('primary_scope', 'general')
            
            geo_text = f"Primary scope: <b>{primary_scope.capitalize()}</b> | "
            geo_text += f"Local: {geo.get('local', 0)}%, "
            geo_text += f"National: {geo.get('national', 0)}%, "
            geo_text += f"International: {geo.get('international', 0)}%"
            
            elements.append(Paragraph(geo_text, self.styles['CustomBody']))
        
        return elements
    
    def _create_score_bar_graphic(self, score, label, reverse_colors=False):
        """Create a horizontal score bar visualization"""
        drawing = Drawing(400, 80)
        
        # Determine color based on score
        if reverse_colors:
            # For metrics where lower is better (like persuasion)
            if score < 30:
                bar_color = colors.HexColor('#10b981')  # Green
            elif score < 60:
                bar_color = colors.HexColor('#f59e0b')  # Yellow
            else:
                bar_color = colors.HexColor('#ef4444')  # Red
        else:
            # For metrics where higher is better
            if score >= 70:
                bar_color = colors.HexColor('#10b981')  # Green
            elif score >= 40:
                bar_color = colors.HexColor('#f59e0b')  # Yellow
            else:
                bar_color = colors.HexColor('#ef4444')  # Red
        
        # Draw background bar
        bar_width = 300
        bar_height = 25
        bar_x = 50
        bar_y = 30
        
        drawing.add(Rect(bar_x, bar_y, bar_width, bar_height, 
                        fillColor=colors.HexColor('#e5e7eb'), 
                        strokeColor=colors.HexColor('#d1d5db'),
                        strokeWidth=1))
        
        # Draw filled portion
        filled_width = (score / 100) * bar_width
        drawing.add(Rect(bar_x, bar_y, filled_width, bar_height, 
                        fillColor=bar_color, 
                        strokeColor=None))
        
        # Add label and score
        drawing.add(String(bar_x, bar_y + bar_height + 10, label, 
                          fontSize=11, textAnchor='start'))
        drawing.add(String(bar_x + bar_width, bar_y + bar_height + 10, f"{score}%", 
                          fontSize=11, textAnchor='end', fillColor=bar_color))
        
        return drawing
    
    def _create_footer(self):
        """Create footer content"""
        elements = []
        
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        elements.append(Spacer(1, 0.2*inch))
        
        footer_text = f"Generated by News Analyzer AI on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        elements.append(Paragraph(footer_text, ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER
        )))
        
        disclaimer = "This analysis is generated by AI and should be used as a supplementary tool. Always verify important information through multiple sources."
        elements.append(Paragraph(disclaimer, ParagraphStyle(
            name='Disclaimer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#9ca3af'),
            alignment=TA_CENTER,
            spaceAfter=20
        )))
        
        return elements
    
    def _add_page_number(self, canvas, doc):
        """Add page numbers to each page"""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#6b7280'))
        canvas.drawString(doc.width / 2 + doc.leftMargin, 0.5 * inch, f"Page {doc.page}")
        canvas.restoreState()
