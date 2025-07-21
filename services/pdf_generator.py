# services/pdf_generator.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from io import BytesIO
import datetime
from typing import Dict, Any

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom styles for the PDF"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceBefore=20,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666')
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#1a73e8'),
            fontName='Helvetica-Bold'
        ))
    
    def generate_analysis_pdf(self, analysis_data: Dict[str, Any]) -> BytesIO:
        """Generate a PDF report from analysis data"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Add title
        elements.append(Paragraph("News Article Analysis Report", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add metadata
        elements.append(Paragraph(f"Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                                self.styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Article Information
        elements.append(Paragraph("Article Information", self.styles['SectionHeading']))
        article_data = [
            ['Title:', analysis_data.get('article', {}).get('title', 'N/A')],
            ['URL:', analysis_data.get('article', {}).get('url', 'N/A')],
            ['Author:', analysis_data.get('author_analysis', {}).get('name', 'Unknown')],
            ['Publication:', analysis_data.get('article', {}).get('domain', 'Unknown')],
            ['Published:', analysis_data.get('article', {}).get('publish_date', 'Unknown')]
        ]
        
        article_table = Table(article_data, colWidths=[1.5*inch, 5*inch])
        article_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (0, -1), 0),
            ('RIGHTPADDING', (0, 0), (0, -1), 10),
        ]))
        elements.append(article_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Trust Score Section
        elements.append(Paragraph("Trust Score Analysis", self.styles['SectionHeading']))
        trust_score = analysis_data.get('trust_score', 0)
        self._add_trust_score_visual(elements, trust_score)
        elements.append(Spacer(1, 0.2*inch))
        
        # Key Metrics Table
        metrics_data = [
            ['Metric', 'Score', 'Status'],
            ['Source Credibility', f"{self._get_source_credibility_score(analysis_data)}/100", 
             self._get_status(self._get_source_credibility_score(analysis_data))],
            ['Author Credibility', f"{analysis_data.get('author_analysis', {}).get('credibility_score', 0)}/100",
             self._get_status(analysis_data.get('author_analysis', {}).get('credibility_score', 0))],
            ['Content Quality', f"{max(0, 100 - analysis_data.get('clickbait_score', 0))}/100",
             self._get_status(max(0, 100 - analysis_data.get('clickbait_score', 0)))],
            ['Bias Level', f"{analysis_data.get('bias_analysis', {}).get('objectivity_score', 0)}/100",
             self._get_status(analysis_data.get('bias_analysis', {}).get('objectivity_score', 0))]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Bias Analysis
        if 'bias_analysis' in analysis_data:
            elements.append(Paragraph("Bias Analysis", self.styles['SectionHeading']))
            bias = analysis_data['bias_analysis']
            
            bias_text = f"""
            <b>Political Lean:</b> {bias.get('overall_bias', 'Neutral')}<br/>
            <b>Bias Score:</b> {abs(bias.get('political_lean', 0))}/100<br/>
            <b>Objectivity:</b> {bias.get('objectivity_score', 0)}/100<br/>
            """
            elements.append(Paragraph(bias_text, self.styles['Normal']))
            
            if bias.get('manipulation_tactics'):
                elements.append(Paragraph("<b>Detected Manipulation Tactics:</b>", self.styles['Normal']))
                for tactic in bias['manipulation_tactics'][:5]:
                    tactic_name = tactic.get('name', tactic) if isinstance(tactic, dict) else tactic
                    elements.append(Paragraph(f"• {tactic_name}", self.styles['Normal']))
            
            elements.append(Spacer(1, 0.3*inch))
        
        # Fact Check Results
        if 'fact_checks' in analysis_data and analysis_data['fact_checks']:
            elements.append(Paragraph("Fact Check Results", self.styles['SectionHeading']))
            fact_checks = analysis_data['fact_checks']
            
            fact_summary = f"""
            <b>Claims Checked:</b> {len(fact_checks)}<br/>
            <b>Verified:</b> {sum(1 for fc in fact_checks if fc.get('verdict') == 'true')}<br/>
            <b>False:</b> {sum(1 for fc in fact_checks if fc.get('verdict') == 'false')}<br/>
            <b>Unverified:</b> {sum(1 for fc in fact_checks if fc.get('verdict') == 'unverified')}<br/>
            """
            elements.append(Paragraph(fact_summary, self.styles['Normal']))
            
            # Add claim details if any false claims
            false_claims = [fc for fc in fact_checks if fc.get('verdict') == 'false']
            if false_claims:
                elements.append(Paragraph("<b>False Claims Detected:</b>", self.styles['Normal']))
                for claim in false_claims[:3]:
                    elements.append(Paragraph(f"• {claim.get('claim', '')[:100]}...", 
                                           self.styles['Normal']))
            
            elements.append(Spacer(1, 0.3*inch))
        
        # Key Points Summary
        if 'article_summary' in analysis_data:
            elements.append(Paragraph("Article Summary", self.styles['SectionHeading']))
            elements.append(Paragraph(analysis_data['article_summary'][:500] + "...", 
                                   self.styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def _get_source_credibility_score(self, analysis_data):
        """Extract source credibility score"""
        source_cred = analysis_data.get('analysis', {}).get('source_credibility', {})
        rating = source_cred.get('rating', 'Unknown')
        
        rating_scores = {
            'High': 85,
            'Medium': 60,
            'Low': 30,
            'Very Low': 10,
            'Unknown': 50
        }
        
        return rating_scores.get(rating, 50)
    
    def _add_trust_score_visual(self, elements, score):
        """Add a visual representation of the trust score"""
        score_color = self._get_score_color(score)
        score_text = f"Overall Trust Score: {score}/100"
        
        elements.append(Paragraph(f'<font color="{score_color}"><b>{score_text}</b></font>', 
                                self.styles['Normal']))
        
        # Add interpretation
        if score >= 80:
            interpretation = "Highly Trustworthy - This article appears to be from a credible source with minimal bias."
        elif score >= 60:
            interpretation = "Generally Trustworthy - Some minor concerns but overall reliable."
        elif score >= 40:
            interpretation = "Questionable - Several red flags detected. Verify information independently."
        else:
            interpretation = "Low Trust - Significant bias or credibility issues detected."
        
        elements.append(Paragraph(f'<i>{interpretation}</i>', self.styles['Normal']))
    
    def _get_score_color(self, score):
        """Get color based on score"""
        if score >= 80:
            return '#4caf50'  # Green
        elif score >= 60:
            return '#ff9800'  # Orange
        else:
            return '#f44336'  # Red
    
    def _get_status(self, score):
        """Get status text based on score"""
        if score >= 80:
            return 'Good'
        elif score >= 60:
            return 'Fair'
        else:
            return 'Poor'
