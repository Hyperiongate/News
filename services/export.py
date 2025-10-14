"""
File: services/export.py
Last Updated: October 14, 2025
Description: Export Service - handles PDF, JSON, and TXT exports
Changes:
- Created as new file for news repository from transcript repository
- Generates professional PDF reports using ReportLab
- Handles JSON and TXT exports
- Creates formatted reports with credibility scores and fact-check details
"""

import os
import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)

# Try to import ReportLab - it's optional
REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
    logger.info("ReportLab loaded successfully - PDF export available")
except ImportError:
    logger.warning("ReportLab not installed - PDF export will not be available")


class ExportService:
    """Main export service that handles multiple export formats"""
    
    def __init__(self):
        self.pdf_available = REPORTLAB_AVAILABLE
        if REPORTLAB_AVAILABLE:
            self.pdf_exporter = PDFExporter()
        else:
            self.pdf_exporter = None
    
    def export_pdf(self, results: Dict, job_id: str) -> str:
        """Export results to PDF format"""
        if not self.pdf_available:
            raise Exception("PDF export not available - ReportLab not installed")
        
        # Add job_id to results for filename generation
        results_with_id = results.copy()
        results_with_id['job_id'] = job_id
        return self.pdf_exporter.export_to_pdf(results_with_id)


class PDFExporter:
    """Generate professional PDF reports for fact check results"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=HexColor('#1f2937'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section headers
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=HexColor('#3b82f6'),
            spaceAfter=12,
            spaceBefore=20
        ))
        
        # Verdict styles
        self.styles.add(ParagraphStyle(
            name='VerdictTrue',
            parent=self.styles['Normal'],
            textColor=HexColor('#10b981'),
            fontSize=11,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='VerdictFalse', 
            parent=self.styles['Normal'],
            textColor=HexColor('#ef4444'),
            fontSize=11,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='VerdictMixed',
            parent=self.styles['Normal'],
            textColor=HexColor('#f59e0b'),
            fontSize=11,
            fontName='Helvetica-Bold'
        ))
    
    def export_to_pdf(self, results: Dict) -> str:
        """Export results to PDF and return the file path"""
        # Generate output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        job_id = results.get('job_id', 'unknown')
        output_filename = f"transcript_analysis_{job_id}_{timestamp}.pdf"
        output_path = os.path.join('exports', output_filename)
        
        # Create exports directory if it doesn't exist
        os.makedirs('exports', exist_ok=True)
        
        # Generate PDF
        if self.generate_pdf(results, output_path):
            return output_path
        else:
            raise Exception("Failed to generate PDF")
    
    def generate_pdf(self, results: Dict, output_path: str) -> bool:
        """Generate PDF report from fact check results"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            
            # Title page
            story.append(Paragraph("Transcript Fact Check Report", self.styles['CustomTitle']))
            story.append(Spacer(1, 0.2*inch))
            
            # Report metadata
            metadata = f"""
            <para align=center>
            <b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
            <b>Source:</b> {results.get('source_type', 'Unknown').title()}<br/>
            <b>Total Claims:</b> {results.get('total_claims', 0)}<br/>
            <b>Verified Claims:</b> {results.get('verified_claims', 0)}
            </para>
            """
            story.append(Paragraph(metadata, self.styles['Normal']))
            story.append(Spacer(1, 0.5*inch))
            
            # Summary section
            if results.get('summary'):
                story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
                summary_text = self._escape_html(results['summary'])
                story.append(Paragraph(summary_text, self.styles['Normal']))
                story.append(Spacer(1, 0.3*inch))
            
            # Credibility Score section
            credibility_score = results.get('credibility_score', {})
            if credibility_score:
                story.append(Paragraph("Credibility Analysis", self.styles['SectionHeader']))
                
                score = credibility_score.get('score', 'N/A')
                label = credibility_score.get('label', 'Unknown')
                description = credibility_score.get('description', '')
                
                story.append(Paragraph(f"<b>Overall Score:</b> {score}/100", self.styles['Normal']))
                story.append(Paragraph(f"<b>Assessment:</b> {label}", self.styles['Normal']))
                if description:
                    story.append(Paragraph(f"<b>Description:</b> {description}", self.styles['Normal']))
                
                story.append(Spacer(1, 0.3*inch))
            
            # Speakers section (if any)
            speakers = results.get('speakers', [])
            if speakers:
                story.append(Paragraph("Speakers Identified", self.styles['SectionHeader']))
                speakers_text = ', '.join(speakers)
                story.append(Paragraph(speakers_text, self.styles['Normal']))
                story.append(Spacer(1, 0.3*inch))
            
            # Topics section (if any)
            topics = results.get('topics', [])
            if topics:
                story.append(Paragraph("Topics Discussed", self.styles['SectionHeader']))
                topics_text = ', '.join([t.title() for t in topics])
                story.append(Paragraph(topics_text, self.styles['Normal']))
                story.append(Spacer(1, 0.3*inch))
            
            # Fact Checks section
            fact_checks = results.get('fact_checks', [])
            if fact_checks:
                story.append(PageBreak())
                story.append(Paragraph("Detailed Fact Checks", self.styles['SectionHeader']))
                story.append(Spacer(1, 0.2*inch))
                
                for i, fc in enumerate(fact_checks, 1):
                    # Claim number and text
                    claim_text = self._escape_html(fc.get('claim', 'Unknown claim'))
                    story.append(Paragraph(f"<b>Claim {i}:</b>", self.styles['Normal']))
                    story.append(Paragraph(claim_text, self.styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
                    
                    # Speaker
                    speaker = fc.get('speaker', 'Unknown')
                    story.append(Paragraph(f"<b>Speaker:</b> {speaker}", self.styles['Normal']))
                    
                    # Verdict
                    verdict = fc.get('verdict', 'unknown').replace('_', ' ').title()
                    verdict_style = self._get_verdict_style(fc.get('verdict', 'unknown'))
                    story.append(Paragraph(f"<b>Verdict:</b> <font color='{verdict_style}'>{verdict}</font>", self.styles['Normal']))
                    
                    # Confidence
                    if fc.get('confidence'):
                        story.append(Paragraph(f"<b>Confidence:</b> {fc['confidence']}%", self.styles['Normal']))
                    
                    # Explanation
                    if fc.get('explanation'):
                        story.append(Spacer(1, 0.1*inch))
                        story.append(Paragraph("<b>Explanation:</b>", self.styles['Normal']))
                        explanation_text = self._escape_html(fc['explanation'])
                        story.append(Paragraph(explanation_text, self.styles['Normal']))
                    
                    # Sources
                    if fc.get('sources'):
                        story.append(Spacer(1, 0.1*inch))
                        sources_text = ', '.join(fc['sources'])
                        story.append(Paragraph(f"<b>Sources:</b> {sources_text}", self.styles['Normal']))
                    
                    story.append(Spacer(1, 0.3*inch))
                    
                    # Add page break every 3 claims
                    if i % 3 == 0 and i < len(fact_checks):
                        story.append(PageBreak())
            
            # Footer
            story.append(PageBreak())
            footer = f"""
            <para align=center>
            <b>Report Generated By:</b> Transcript Fact Checker<br/>
            <b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
            <i>This report was automatically generated using AI-powered fact-checking.</i>
            </para>
            """
            story.append(Paragraph(footer, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            logger.info(f"PDF generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"PDF generation error: {str(e)}")
            return False
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        if not text:
            return ''
        return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))
    
    def _get_verdict_style(self, verdict: str) -> str:
        """Get color for verdict"""
        verdict_colors = {
            'true': '#10b981',
            'mostly_true': '#34d399',
            'nearly_true': '#6ee7b7',
            'false': '#ef4444',
            'mostly_false': '#f87171',
            'misleading': '#f59e0b',
            'exaggeration': '#fbbf24',
            'mixed': '#f59e0b',
            'opinion': '#6366f1',
            'unverified': '#8b5cf6',
            'needs_context': '#8b5cf6',
            'empty_rhetoric': '#94a3b8',
            'unsubstantiated_prediction': '#a78bfa'
        }
        return verdict_colors.get(verdict, '#6b7280')
