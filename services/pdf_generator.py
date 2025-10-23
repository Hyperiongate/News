# services/pdf_generator.py
"""
PDF Generation Service - v2.2
Creates professional PDF reports from analysis results

CHANGE LOG:
- 2025-10-23: v2.2 - FIXED: Bias graphic now displays as horizontal straight line
  * New method: _create_bias_bar_graphic()
  * Replaced curved/circular bias meter with horizontal color-coded bar
  * 5 colored zones: Red-Orange-Green-Orange-Red (matching web UI)
  * Clean, professional straight-line design
  * Position marker shows exact bias location
  * Labels below bar for clarity

Previous versions:
- v2.1 - Added bias section
- v2.0 - Enhanced PDF generation
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
    from reportlab.graphics.shapes import Drawing, Circle, Rect, String, Line
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
            textColor=colors.HexColor('#065f46'),
            backColor=colors.HexColor('#d1fae5'),
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
            backColor=colors.HexColor('#dbeafe'),
            borderWidth=1,
            borderColor=colors.HexColor('#3b82f6'),
            borderPadding=8,
            spaceAfter=12
        ))
    
    def _create_cover_page(self, data):
        """Create cover page"""
        elements = []
        
        # Title
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph("News Analysis Report", self.styles['CustomTitle']))
        
        # Article info
        article = data.get('article', {})
        title = article.get('title', 'Unknown Article')
        domain = article.get('domain', 'Unknown Source')
        
        elements.append(Paragraph(f"<i>{title}</i>", self.styles['Subtitle']))
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(f"Source: {domain}", self.styles['Subtitle']))
        
        # Trust score
        trust_score = data.get('trust_score', 0)
        elements.append(Spacer(1, 1*inch))
        elements.append(self._create_trust_score_graphic(trust_score))
        
        # Date
        elements.append(Spacer(1, 1*inch))
        date_str = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(f"Generated: {date_str}", self.styles['Subtitle']))
        
        return elements
    
    def _create_executive_summary(self, data):
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Trust score assessment
        trust_score = data.get('trust_score', 0)
        if trust_score >= 70:
            assessment = "This article demonstrates strong credibility and reliability."
            style = self.styles['Success']
        elif trust_score >= 40:
            assessment = "This article shows moderate credibility. Exercise caution with key facts."
            style = self.styles['Info']
        else:
            assessment = "This article raises significant credibility concerns. Verify all information independently."
            style = self.styles['Alert']
        
        elements.append(Paragraph(assessment, style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Key metrics table
        article = data.get('article', {})
        metrics_data = [
            ['<b>Metric</b>', '<b>Score</b>'],
            ['Overall Trust Score', f'{trust_score}/100'],
            ['Source Credibility', f"{data.get('source_credibility', {}).get('score', 'N/A')}"],
            ['Author Credibility', f"{data.get('author_info', {}).get('credibility_score', 'N/A')}"],
            ['Fact Check Score', f"{data.get('fact_check_summary', {}).get('accuracy', 'N/A')}"],
            ['Transparency', f"{data.get('transparency_analysis', {}).get('score', 'N/A')}%"]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db'))
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary text
        summary_text = data.get('summary', 'Analysis complete.')
        elements.append(Paragraph(summary_text, self.styles['CustomBody']))
        
        return elements
    
    def _create_bias_section(self, bias_data):
        """
        Create bias analysis section with HORIZONTAL STRAIGHT-LINE GRAPHIC
        v2.2 - October 23, 2025
        """
        elements = []
        
        elements.append(Paragraph("Political Bias Analysis", self.styles['SectionHeader']))
        
        # Add the NEW horizontal bias bar graphic
        elements.append(self._create_bias_bar_graphic(bias_data))
        elements.append(Spacer(1, 0.3*inch))
        
        # Bias assessment
        political_lean = bias_data.get('political_lean', 0)
        political_label = bias_data.get('political_label', 'Center')
        objectivity_score = bias_data.get('objectivity_score', 50)
        
        elements.append(Paragraph(f"<b>Political Lean:</b> {political_label}", self.styles['CustomBody']))
        elements.append(Paragraph(f"<b>Objectivity Score:</b> {objectivity_score}/100", self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Interpretation
        if abs(political_lean) < 0.2:
            interpretation = "The article demonstrates balanced coverage with minimal political bias."
            style = self.styles['Success']
        elif abs(political_lean) < 0.5:
            direction = "left-leaning" if political_lean < 0 else "right-leaning"
            interpretation = f"The article shows noticeable {direction} perspective."
            style = self.styles['Info']
        else:
            direction = "left-leaning" if political_lean < 0 else "right-leaning"
            interpretation = f"The article demonstrates significant {direction} bias."
            style = self.styles['Alert']
        
        elements.append(Paragraph(interpretation, style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Bias factors
        if bias_data.get('bias_factors'):
            elements.append(Paragraph("Bias Indicators Detected:", self.styles['SubsectionHeader']))
            for factor in bias_data['bias_factors'][:5]:  # Limit to 5
                if isinstance(factor, dict):
                    text = factor.get('description', str(factor))
                else:
                    text = str(factor)
                elements.append(Paragraph(f"• {text}", self.styles['CustomBody']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Language patterns
        if bias_data.get('language_patterns'):
            elements.append(Paragraph("Language Patterns:", self.styles['SubsectionHeader']))
            for pattern in bias_data['language_patterns'][:3]:  # Limit to 3
                if isinstance(pattern, dict):
                    text = pattern.get('name', str(pattern))
                else:
                    text = str(pattern)
                elements.append(Paragraph(f"• {text}", self.styles['CustomBody']))
        
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
    
    def _create_bias_bar_graphic(self, bias_data):
        """
        Create HORIZONTAL STRAIGHT-LINE bias bar graphic for PDF
        v2.2 - October 23, 2025
        
        Args:
            bias_data: Bias analysis data with political_lean, political_label
            
        Returns:
            Drawing object with horizontal bias bar visualization
        """
        if not bias_data:
            # Return empty drawing if no data
            return Drawing(450, 120)
        
        # Get bias position data
        political_lean = bias_data.get('political_lean', 0)
        political_label = bias_data.get('political_label', 'Center')
        objectivity_score = bias_data.get('objectivity_score', 50)
        
        # Convert political lean (-1 to +1) to horizontal position (0-450)
        # -1 (far left) = 0px, 0 (center) = 225px, +1 (far right) = 450px
        bar_width = 450
        marker_position = int((political_lean + 1) * (bar_width / 2))
        marker_position = max(0, min(bar_width, marker_position))  # Clamp to 0-450 range
        
        # Create drawing
        drawing = Drawing(bar_width, 120)
        
        # Define colors
        far_left_color = colors.HexColor('#dc2626')     # Red
        left_color = colors.HexColor('#ef4444')          # Light Red
        left_orange = colors.HexColor('#f59e0b')         # Orange
        center_color = colors.HexColor('#10b981')        # Green
        right_orange = colors.HexColor('#f59e0b')        # Orange
        right_color = colors.HexColor('#ef4444')         # Light Red
        far_right_color = colors.HexColor('#dc2626')    # Red
        
        # Bar dimensions
        bar_height = 40
        bar_y = 60
        
        # Draw 5 colored zones as rectangles (straight horizontal bar)
        zone_width = bar_width / 5
        
        # Zone 1: Far Left (Red) 0-20%
        drawing.add(Rect(0, bar_y, zone_width, bar_height, 
                        fillColor=far_left_color, strokeColor=None))
        
        # Zone 2: Left (Orange-Red) 20-40%
        drawing.add(Rect(zone_width, bar_y, zone_width, bar_height, 
                        fillColor=left_color, strokeColor=None))
        
        # Zone 3: Center (Green) 40-60%
        drawing.add(Rect(zone_width*2, bar_y, zone_width, bar_height, 
                        fillColor=center_color, strokeColor=None))
        
        # Zone 4: Right (Orange-Red) 60-80%
        drawing.add(Rect(zone_width*3, bar_y, zone_width, bar_height, 
                        fillColor=right_color, strokeColor=None))
        
        # Zone 5: Far Right (Red) 80-100%
        drawing.add(Rect(zone_width*4, bar_y, zone_width, bar_height, 
                        fillColor=far_right_color, strokeColor=None))
        
        # Add position marker (dark circle)
        marker_radius = 8
        drawing.add(Circle(marker_position, bar_y + bar_height/2, marker_radius, 
                          fillColor=colors.HexColor('#1e293b'), 
                          strokeColor=colors.white, strokeWidth=2))
        
        # Add labels below the bar
        label_y = bar_y - 10
        label_font_size = 9
        
        drawing.add(String(0, label_y, 'Far Left', 
                          fontSize=label_font_size, fillColor=far_left_color, 
                          fontName='Helvetica-Bold'))
        
        drawing.add(String(zone_width + 20, label_y, 'Left', 
                          fontSize=label_font_size, fillColor=left_color, 
                          fontName='Helvetica-Bold'))
        
        drawing.add(String(zone_width*2 + 25, label_y, 'CENTER', 
                          fontSize=label_font_size, fillColor=center_color, 
                          fontName='Helvetica-Bold'))
        
        drawing.add(String(zone_width*3 + 20, label_y, 'Right', 
                          fontSize=label_font_size, fillColor=right_color, 
                          fontName='Helvetica-Bold'))
        
        drawing.add(String(zone_width*4 + 10, label_y, 'Far Right', 
                          fontSize=label_font_size, fillColor=far_right_color, 
                          fontName='Helvetica-Bold'))
        
        # Add detected position label above the bar
        position_y = bar_y + bar_height + 15
        drawing.add(String(bar_width/2, position_y, f'Detected: {political_label}', 
                          textAnchor='middle', fontSize=11, 
                          fillColor=colors.HexColor('#1e293b'), 
                          fontName='Helvetica-Bold'))
        
        # Add objectivity score below labels
        score_y = label_y - 15
        drawing.add(String(bar_width/2, score_y, f'Objectivity: {objectivity_score}/100', 
                          textAnchor='middle', fontSize=10, 
                          fillColor=colors.HexColor('#374151')))
        
        return drawing
    
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

# This file is not truncated
