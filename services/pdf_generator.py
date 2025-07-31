# services/pdf_generator.py
"""
PDF Generation Service
Creates professional PDF reports from analysis results
"""

import io
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import reportlab
REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY, TA_LEFT
    from reportlab.pdfgen import canvas
    from reportlab.graphics.shapes import Drawing, Circle, Rect, String
    from reportlab.graphics.charts.piecharts import Pie
    REPORTLAB_AVAILABLE = True
    logger.info("ReportLab loaded successfully")
except ImportError as e:
    logger.warning(f"ReportLab not installed - PDF generation disabled: {e}")

class PDFGenerator:
    """Generate PDF reports from analysis results"""
    
    def __init__(self):
        """Initialize PDF generator"""
        self.available = REPORTLAB_AVAILABLE
        
        if self.available:
            self.styles = getSampleStyleSheet()
            self._setup_custom_styles()
        else:
            logger.warning("PDF generation not available - reportlab not installed")
    
    def generate_report(self, analysis_results):
        """
        Generate PDF report - main entry point for app.py
        
        Args:
            analysis_results: Dictionary containing analysis results
            
        Returns:
            Path to generated PDF file or None if not available
        """
        if not self.available:
            logger.error("Cannot generate PDF - reportlab not installed")
            return None
        
        try:
            # Generate the PDF in memory
            pdf_buffer = self.generate_analysis_pdf(analysis_results)
            
            # Save to temporary file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"news_analysis_{timestamp}.pdf"
            
            # Use /tmp directory for temporary files
            filepath = os.path.join('/tmp', filename)
            
            # Write buffer to file
            with open(filepath, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            
            logger.info(f"PDF generated successfully: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}", exc_info=True)
            return None
    
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
        
        # Add comprehensive bias analysis section if available
        if analysis_data.get('bias_analysis'):
            story.extend(self._create_bias_section(analysis_data.get('bias_analysis', {})))
            story.append(PageBreak())
        
        # Add fact checking section if available
        if analysis_data.get('fact_checks'):
            story.extend(self._create_fact_check_section(
                analysis_data.get('fact_checks', []), 
                analysis_data.get('fact_check_summary')
            ))
            story.append(PageBreak())
        
        # Add author analysis section if available
        if analysis_data.get('author_info'):
            story.extend(self._create_author_section(analysis_data.get('author_info', {})))
            story.append(PageBreak())
        
        # Add other analysis sections
        story.extend(self._create_additional_sections(analysis_data))
        
        # Add footer
        story.extend(self._create_footer())
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        buffer.seek(0)
        
        return buffer
    
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
            spaceBefore=20
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
            spaceAfter=12
        ))
    
    def _create_cover_page(self, data):
        """Create the cover page"""
        elements = []
        
        # Title
        elements.append(Paragraph("News Analysis Report", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Article info
        article = data.get('article', {})
        if article.get('title'):
            elements.append(Paragraph(article['title'], self.styles['Subtitle']))
        
        # Metadata table
        metadata = []
        if article.get('author'):
            metadata.append(['Author:', article['author']])
        if article.get('domain'):
            metadata.append(['Source:', article['domain']])
        if article.get('date'):
            metadata.append(['Published:', article['date']])
        metadata.append(['Analysis Date:', datetime.now().strftime('%B %d, %Y')])
        
        if metadata:
            t = Table(metadata, colWidths=[2*inch, 4*inch])
            t.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(Spacer(1, 0.3*inch))
            elements.append(t)
        
        # Trust Score
        elements.append(Spacer(1, 0.5*inch))
        trust_score = data.get('trust_score', 0)
        elements.append(self._create_trust_score_graphic(trust_score))
        
        # Key metrics summary
        elements.append(Spacer(1, 0.5*inch))
        metrics = []
        
        if data.get('bias_analysis'):
            bias = data['bias_analysis']
            political_lean = bias.get('political_lean', 0)
            if political_lean < -20:
                lean_text = "Left-leaning"
            elif political_lean > 20:
                lean_text = "Right-leaning"
            else:
                lean_text = "Center/Neutral"
            metrics.append(['Political Bias:', lean_text])
        
        if data.get('clickbait_analysis'):
            score = data['clickbait_analysis'].get('score', 0)
            level = 'Low' if score < 30 else 'Medium' if score < 60 else 'High'
            metrics.append(['Clickbait Level:', f"{level} ({score}%)"])
        
        if data.get('source_credibility'):
            metrics.append(['Source Credibility:', data['source_credibility'].get('credibility', 'Unknown')])
        
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
            ]))
            elements.append(t)
        
        return elements
    
    def _create_executive_summary(self, data):
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Trust assessment
        trust_score = data.get('trust_score', 0)
        if trust_score >= 70:
            trust_text = "This article demonstrates high credibility with reliable sourcing and minimal bias."
            style = self.styles['Success']
        elif trust_score >= 40:
            trust_text = "This article shows moderate credibility. Some caution is advised when interpreting claims."
            style = self.styles['CustomBody']
        else:
            trust_text = "This article has significant credibility concerns. Verify all claims through independent sources."
            style = self.styles['Alert']
        
        elements.append(Paragraph(trust_text, style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Key findings
        elements.append(Paragraph("Key Findings", self.styles['SubsectionHeader']))
        
        findings = []
        
        # Source credibility
        if data.get('source_credibility'):
            cred = data['source_credibility']
            findings.append(f"• Source Credibility: {cred.get('credibility', 'Unknown')} - {cred.get('description', '')}")
        
        # Bias analysis
        if data.get('bias_analysis'):
            bias = data['bias_analysis']
            findings.append(f"• Political Bias: {abs(bias.get('political_lean', 0))}% " +
                          ("left" if bias.get('political_lean', 0) < 0 else "right" if bias.get('political_lean', 0) > 0 else "center"))
        
        # Transparency
        if data.get('transparency_analysis'):
            trans = data['transparency_analysis']
            findings.append(f"• Transparency Score: {trans.get('score', 0)}%")
        
        for finding in findings:
            elements.append(Paragraph(finding, self.styles['CustomBody']))
        
        return elements
    
    def _create_bias_section(self, bias_data):
        """Create bias analysis section"""
        elements = []
        
        elements.append(Paragraph("Bias Analysis", self.styles['SectionHeader']))
        
        # Political lean
        lean = bias_data.get('political_lean', 0)
        if lean < -20:
            lean_text = "Left-leaning"
        elif lean > 20:
            lean_text = "Right-leaning"
        else:
            lean_text = "Center/Neutral"
        
        elements.append(Paragraph(f"<b>Political Orientation:</b> {lean_text} ({lean:+d})", self.styles['CustomBody']))
        
        # Other bias metrics
        metrics = [
            ['Metric', 'Value'],
            ['Objectivity Score', f"{bias_data.get('objectivity_score', 0)}%"],
            ['Opinion Content', f"{bias_data.get('opinion_percentage', 0)}%"],
            ['Emotional Language', f"{bias_data.get('emotional_score', 0)}%"]
        ]
        
        t = Table(metrics, colWidths=[2.5*inch, 2*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(t)
        
        # Manipulation tactics
        if bias_data.get('manipulation_tactics'):
            elements.append(Paragraph("Manipulation Tactics Detected", self.styles['SubsectionHeader']))
            for tactic in bias_data['manipulation_tactics'][:5]:  # Limit to 5
                if isinstance(tactic, dict):
                    text = tactic.get('name', str(tactic))
                else:
                    text = str(tactic)
                elements.append(Paragraph(f"• {text}", self.styles['CustomBody']))
        
        return elements
    
    def _create_fact_check_section(self, fact_checks, summary=None):
        """Create fact checking section"""
        elements = []
        
        elements.append(Paragraph("Fact Check Results", self.styles['SectionHeader']))
        
        if summary:
            elements.append(Paragraph(summary, self.styles['Info']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Statistics
        total = len(fact_checks)
        verified = sum(1 for fc in fact_checks if fc.get('verdict', '').lower() in ['true', 'verified'])
        
        elements.append(Paragraph(f"<b>Total Claims Checked:</b> {total}", self.styles['CustomBody']))
        elements.append(Paragraph(f"<b>Verified as True:</b> {verified} ({int(verified/total*100) if total > 0 else 0}%)", 
                                self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Individual checks (limit to first 5)
        for i, fc in enumerate(fact_checks[:5]):
            claim = fc.get('claim', fc.get('text', 'Unknown claim'))
            verdict = fc.get('verdict', 'Unverified')
            
            elements.append(Paragraph(f"<b>Claim {i+1}:</b> \"{claim}\"", self.styles['CustomBody']))
            
            # Color based on verdict
            if verdict.lower() in ['true', 'verified']:
                color = colors.HexColor('#10b981')
            elif verdict.lower() in ['false', 'incorrect']:
                color = colors.HexColor('#ef4444')
            else:
                color = colors.HexColor('#f59e0b')
            
            elements.append(Paragraph(f"Verdict: <font color='{color}'><b>{verdict}</b></font>", 
                                    self.styles['CustomBody']))
            
            if fc.get('explanation'):
                elements.append(Paragraph(f"Explanation: {fc['explanation']}", self.styles['CustomBody']))
            
            elements.append(Spacer(1, 0.1*inch))
        
        if len(fact_checks) > 5:
            elements.append(Paragraph(f"<i>... and {len(fact_checks) - 5} more claims</i>", self.styles['CustomBody']))
        
        return elements
    
    def _create_author_section(self, author_data):
        """Create author analysis section"""
        elements = []
        
        elements.append(Paragraph("Author Analysis", self.styles['SectionHeader']))
        
        # Author name
        elements.append(Paragraph(f"<b>Author:</b> {author_data.get('name', 'Unknown')}", self.styles['CustomBody']))
        
        if not author_data.get('found'):
            elements.append(Paragraph("No detailed author information could be found.", self.styles['Alert']))
            return elements
        
        # Credibility score
        cred_score = author_data.get('credibility_score', 0)
        elements.append(Paragraph(f"<b>Credibility Score:</b> {cred_score}/100", self.styles['CustomBody']))
        
        # Bio if available
        if author_data.get('bio'):
            elements.append(Paragraph("<b>Biography:</b>", self.styles['SubsectionHeader']))
            elements.append(Paragraph(author_data['bio'], self.styles['CustomBody']))
        
        # Professional info
        if author_data.get('professional_info'):
            prof = author_data['professional_info']
            if prof.get('current_position'):
                elements.append(Paragraph(f"<b>Position:</b> {prof['current_position']}", self.styles['CustomBody']))
            if prof.get('outlets'):
                elements.append(Paragraph(f"<b>Associated Outlets:</b> {', '.join(prof['outlets'][:3])}", 
                                        self.styles['CustomBody']))
        
        return elements
    
    def _create_additional_sections(self, data):
        """Create additional analysis sections"""
        elements = []
        
        # Transparency section
        if data.get('transparency_analysis'):
            trans = data['transparency_analysis']
            elements.append(Paragraph("Transparency Analysis", self.styles['SectionHeader']))
            elements.append(Paragraph(f"<b>Transparency Score:</b> {trans.get('score', 0)}%", 
                                    self.styles['CustomBody']))
            
            if trans.get('strengths'):
                elements.append(Paragraph("<b>Strengths:</b>", self.styles['CustomBody']))
                for strength in trans['strengths'][:3]:
                    elements.append(Paragraph(f"• {strength}", self.styles['CustomBody']))
            
            if trans.get('issues'):
                elements.append(Paragraph("<b>Issues:</b>", self.styles['CustomBody']))
                for issue in trans['issues'][:3]:
                    elements.append(Paragraph(f"• {issue}", self.styles['CustomBody']))
            
            elements.append(Spacer(1, 0.3*inch))
        
        # Clickbait section
        if data.get('clickbait_analysis'):
            click = data['clickbait_analysis']
            elements.append(Paragraph("Clickbait Analysis", self.styles['SectionHeader']))
            
            score = click.get('score', 0)
            if score < 30:
                assessment = "The headline appears genuine and informative."
                style = self.styles['Success']
            elif score < 60:
                assessment = "The headline shows some sensational elements."
                style = self.styles['CustomBody']
            else:
                assessment = "The headline uses significant clickbait tactics."
                style = self.styles['Alert']
            
            elements.append(Paragraph(f"<b>Clickbait Score:</b> {score}%", self.styles['CustomBody']))
            elements.append(Paragraph(assessment, style))
            elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_footer(self):
        """Create footer elements"""
        elements = []
        
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb'), 
                                  spaceAfter=0.2*inch))
        
        footer_text = f"Generated by News Analyzer on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        elements.append(Paragraph(footer_text, ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER
        )))
        
        disclaimer = "This analysis is provided for informational purposes only. Always verify important information through multiple sources."
        elements.append(Paragraph(disclaimer, ParagraphStyle(
            name='Disclaimer',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor('#9ca3af'),
            alignment=TA_CENTER,
            spaceAfter=20
        )))
        
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
        
        # Score text in center
        drawing.add(String(200, 100, f'{score}%', textAnchor='middle', 
                          fontSize=36, fontName='Helvetica-Bold', fillColor=color))
        
        # Label
        drawing.add(String(200, 50, label, textAnchor='middle', fontSize=16, fillColor=color))
        
        return drawing
    
    def _add_page_number(self, canvas_obj, doc):
        """Add page numbers to PDF"""
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(colors.HexColor('#6b7280'))
        canvas_obj.drawCentredString(letter[0]/2, 30, f"Page {doc.page}")
        canvas_obj.restoreState()
