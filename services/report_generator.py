"""
FILE: services/report_generator.py
LOCATION: news/services/report_generator.py
PURPOSE: Generate PDF reports for news analysis (future monetization feature)
"""

import io
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class ReportGenerator:
    """Generate professional PDF reports for analysis results"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom styles for the report"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=HexColor('#1f2937'),
            spaceAfter=30
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#6366f1'),
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='TrustScore',
            parent=self.styles['Normal'],
            fontSize=36,
            textColor=HexColor('#10b981'),
            alignment=1  # Center
        ))
    
    def generate_pdf(self, analysis_data):
        """
        Generate a PDF report from analysis data
        
        Args:
            analysis_data: Dictionary containing analysis results
            
        Returns:
            bytes: PDF file content
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("News Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata
        article = analysis_data.get('article', {})
        if article.get('title'):
            story.append(Paragraph(f"<b>Article:</b> {article['title']}", self.styles['Normal']))
        if article.get('author'):
            story.append(Paragraph(f"<b>Author:</b> {article['author']}", self.styles['Normal']))
        if article.get('domain'):
            story.append(Paragraph(f"<b>Source:</b> {article['domain']}", self.styles['Normal']))
        
        story.append(Paragraph(f"<b>Analysis Date:</b> {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Trust Score
        trust_score = analysis_data.get('trust_score', 0)
        story.append(Paragraph("Overall Trust Score", self.styles['SectionHeader']))
        story.append(Paragraph(f"{trust_score}%", self.styles['TrustScore']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        if analysis_data.get('summary'):
            story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
            story.append(Paragraph(analysis_data['summary'], self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Source Credibility
        if analysis_data.get('source_credibility'):
            cred = analysis_data['source_credibility']
            story.append(Paragraph("Source Credibility", self.styles['SectionHeader']))
            story.append(Paragraph(f"Credibility Rating: {cred.get('credibility', 'Unknown')}", self.styles['Normal']))
            story.append(Paragraph(f"Political Bias: {cred.get('bias', 'Unknown')}", self.styles['Normal']))
            story.append(Paragraph(f"Source Type: {cred.get('type', 'Unknown')}", self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Bias Analysis
        bias_score = analysis_data.get('bias_score', 0)
        story.append(Paragraph("Bias Analysis", self.styles['SectionHeader']))
        bias_label = 'Center/Neutral'
        if bias_score < -0.3:
            bias_label = 'Left-leaning'
        elif bias_score > 0.3:
            bias_label = 'Right-leaning'
        story.append(Paragraph(f"Political Lean: {bias_label}", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Manipulation Tactics
        if analysis_data.get('manipulation_tactics'):
            story.append(Paragraph("Manipulation Tactics Detected", self.styles['SectionHeader']))
            for tactic in analysis_data['manipulation_tactics']:
                story.append(Paragraph(f"• {tactic}", self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Key Claims and Fact Checks
        if analysis_data.get('key_claims'):
            story.append(Paragraph("Key Claims Analysis", self.styles['SectionHeader']))
            fact_checks = analysis_data.get('fact_checks', [])
            
            for i, claim in enumerate(analysis_data['key_claims']):
                story.append(Paragraph(f"<b>Claim {i+1}:</b> {claim}", self.styles['Normal']))
                
                if i < len(fact_checks):
                    check = fact_checks[i]
                    verdict = check.get('verdict', 'unverified').upper()
                    story.append(Paragraph(f"Verdict: {verdict}", self.styles['Normal']))
                    if check.get('explanation'):
                        story.append(Paragraph(f"Explanation: {check['explanation']}", self.styles['Normal']))
                
                story.append(Spacer(1, 0.1*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("Generated by Facts & Fakes AI - News Analyzer", self.styles['Normal']))
        story.append(Paragraph("factsandfakes.ai", self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer.getvalue()
    
    def generate_batch_report(self, analyses):
        """Generate a report for multiple analyses (future feature)"""
        # TODO: Implement batch reporting for enterprise users
        pass
