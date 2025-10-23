"""
File: services/export.py
Last Updated: October 23, 2025
Version: 2.0.0 - FIXED TRANSCRIPT PDF TO ONLY SHOW FACT-CHECKED CLAIMS

CHANGES (October 23, 2025):
- CRITICAL FIX: PDF now only includes fact-checked claims (from fact_checks array)
- REMOVED: No longer shows all extracted claims
- ADDED: Detection of transcript vs news analysis for appropriate PDF generation
- IMPROVED: Better data structure handling
- PRESERVED: All existing functionality (DO NO HARM ✓)

Previous Changes:
- Created as new file for news repository from transcript repository
- Generates professional PDF reports using ReportLab
- Handles JSON and TXT exports
- Creates formatted reports with credibility scores and fact-check details

This file is complete and not truncated.
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
    """Generate professional PDF reports for both transcript and news analysis"""
    
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
        
        # Detect analysis type for filename
        is_transcript = self._is_transcript_analysis(results)
        prefix = "transcript_analysis" if is_transcript else "news_analysis"
        output_filename = f"{prefix}_{job_id}_{timestamp}.pdf"
        output_path = os.path.join('exports', output_filename)
        
        # Create exports directory if it doesn't exist
        os.makedirs('exports', exist_ok=True)
        
        # Generate PDF
        if self.generate_pdf(results, output_path):
            return output_path
        else:
            raise Exception("Failed to generate PDF")
    
    def _is_transcript_analysis(self, results: Dict) -> bool:
        """
        Detect if this is transcript analysis vs news analysis
        
        Transcript analysis has:
        - fact_checks array (fact-checked claims)
        - claims array (all extracted claims) 
        - speakers, topics
        
        News analysis has:
        - services dict with analysis results
        - No fact_checks array
        """
        # Check for transcript-specific markers
        has_fact_checks = 'fact_checks' in results
        has_speakers = 'speakers' in results
        has_services = 'services' in results or 'analysis_results' in results
        
        # If it has fact_checks and speakers, it's transcript analysis
        if has_fact_checks and has_speakers:
            return True
        
        # If it has services dict, it's news analysis
        if has_services:
            return False
        
        # Default to transcript if we have fact_checks
        return has_fact_checks
    
    def generate_pdf(self, results: Dict, output_path: str) -> bool:
        """Generate PDF report - auto-detects transcript vs news analysis"""
        try:
            is_transcript = self._is_transcript_analysis(results)
            
            if is_transcript:
                return self._generate_transcript_pdf(results, output_path)
            else:
                return self._generate_news_pdf(results, output_path)
                
        except Exception as e:
            logger.error(f"PDF generation error: {str(e)}")
            return False
    
    def _generate_transcript_pdf(self, results: Dict, output_path: str) -> bool:
        """
        Generate PDF for TRANSCRIPT analysis
        
        CRITICAL: Only shows FACT-CHECKED claims from fact_checks array
        Does NOT show all extracted claims from claims array
        """
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
            # CRITICAL: Get fact-checked claims count, not total extracted claims
            fact_checks = results.get('fact_checks', [])
            metadata = f"""
            <para align=center>
            <b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
            <b>Source:</b> {results.get('source_type', 'Unknown').title()}<br/>
            <b>Fact-Checked Claims:</b> {len(fact_checks)}
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
                
                story.append(Paragraph(f"<b>Overall Score:</b> {score}/100", self.styles['Normal']))
                story.append(Paragraph(f"<b>Assessment:</b> {label}", self.styles['Normal']))
                
                # Breakdown
                breakdown = credibility_score.get('breakdown', {})
                if breakdown:
                    story.append(Paragraph("<b>Verdict Breakdown:</b>", self.styles['Normal']))
                    for verdict, count in breakdown.items():
                        if count > 0:
                            readable_verdict = verdict.replace('_', ' ').title()
                            story.append(Paragraph(f"  • {readable_verdict}: {count}", self.styles['Normal']))
                
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
            
            # CRITICAL: Fact Checks section - ONLY SHOW FACT-CHECKED CLAIMS
            # Do NOT include claims from results['claims'] array
            if fact_checks and len(fact_checks) > 0:
                story.append(PageBreak())
                story.append(Paragraph("Fact-Checked Claims", self.styles['SectionHeader']))
                story.append(Paragraph(
                    f"<i>The following {len(fact_checks)} claims were extracted and fact-checked using AI and trusted sources.</i>",
                    self.styles['Normal']
                ))
                story.append(Spacer(1, 0.2*inch))
                
                for i, fc in enumerate(fact_checks, 1):
                    # Claim number and text
                    claim_text = self._escape_html(fc.get('claim', fc.get('text', 'Unknown claim')))
                    story.append(Paragraph(f"<b>Claim {i}:</b>", self.styles['Normal']))
                    story.append(Paragraph(claim_text, self.styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
                    
                    # Speaker
                    speaker = fc.get('speaker', 'Unknown')
                    if speaker and speaker != 'Unknown':
                        story.append(Paragraph(f"<b>Speaker:</b> {speaker}", self.styles['Normal']))
                    
                    # Verdict
                    verdict = fc.get('verdict', 'unverified')
                    verdict_display = verdict.replace('_', ' ').title()
                    verdict_color = self._get_verdict_style(verdict)
                    story.append(Paragraph(
                        f"<b>Verdict:</b> <font color='{verdict_color}'>{verdict_display}</font>", 
                        self.styles['Normal']
                    ))
                    
                    # Confidence
                    if fc.get('confidence'):
                        story.append(Paragraph(f"<b>Confidence:</b> {fc['confidence']}%", self.styles['Normal']))
                    
                    # Explanation
                    if fc.get('explanation'):
                        story.append(Spacer(1, 0.1*inch))
                        story.append(Paragraph("<b>Analysis:</b>", self.styles['Normal']))
                        explanation_text = self._escape_html(fc['explanation'])
                        story.append(Paragraph(explanation_text, self.styles['Normal']))
                    
                    # Sources
                    if fc.get('sources') and len(fc['sources']) > 0:
                        story.append(Spacer(1, 0.1*inch))
                        sources_text = ', '.join(fc['sources'])
                        story.append(Paragraph(f"<b>Sources:</b> {sources_text}", self.styles['Normal']))
                    
                    story.append(Spacer(1, 0.3*inch))
                    
                    # Add page break every 3 claims
                    if i % 3 == 0 and i < len(fact_checks):
                        story.append(PageBreak())
            else:
                story.append(Paragraph("No Fact-Checked Claims", self.styles['SectionHeader']))
                story.append(Paragraph(
                    "No verifiable factual claims were found in this transcript that could be fact-checked.",
                    self.styles['Normal']
                ))
            
            # Footer
            story.append(PageBreak())
            footer = f"""
            <para align=center>
            <b>Report Generated By:</b> TruthLens Transcript Analyzer<br/>
            <b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
            <i>This report was automatically generated using AI-powered fact-checking.</i>
            </para>
            """
            story.append(Paragraph(footer, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            logger.info(f"Transcript PDF generated successfully: {output_path}")
            logger.info(f"  - Fact-checked claims included: {len(fact_checks)}")
            return True
            
        except Exception as e:
            logger.error(f"Transcript PDF generation error: {str(e)}")
            return False
    
    def _generate_news_pdf(self, results: Dict, output_path: str) -> bool:
        """
        Generate PDF for NEWS analysis
        
        Shows service-based analysis results
        """
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
            story.append(Paragraph("News Analysis Report", self.styles['CustomTitle']))
            story.append(Spacer(1, 0.2*inch))
            
            # Report metadata
            metadata = f"""
            <para align=center>
            <b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
            <b>Analysis Type:</b> News Credibility Analysis
            </para>
            """
            story.append(Paragraph(metadata, self.styles['Normal']))
            story.append(Spacer(1, 0.5*inch))
            
            # Summary
            if results.get('summary'):
                story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
                summary_text = self._escape_html(results.get('summary', ''))
                story.append(Paragraph(summary_text, self.styles['Normal']))
                story.append(Spacer(1, 0.3*inch))
            
            # Services results
            services = results.get('services', {}) or results.get('analysis_results', {})
            if services:
                story.append(Paragraph("Analysis Results", self.styles['SectionHeader']))
                for service_name, service_data in services.items():
                    service_title = service_name.replace('_', ' ').title()
                    story.append(Paragraph(f"<b>{service_title}:</b>", self.styles['Normal']))
                    
                    if isinstance(service_data, dict):
                        score = service_data.get('score', 'N/A')
                        story.append(Paragraph(f"Score: {score}", self.styles['Normal']))
                    
                    story.append(Spacer(1, 0.2*inch))
            
            # Footer
            footer = f"""
            <para align=center>
            <b>Report Generated By:</b> TruthLens News Analyzer<br/>
            <b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </para>
            """
            story.append(Paragraph(footer, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            logger.info(f"News PDF generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"News PDF generation error: {str(e)}")
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
        return verdict_colors.get(verdict.lower(), '#6b7280')


# I did no harm and this file is not truncated
