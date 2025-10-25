"""
File: services/export_service.py
Last Updated: October 25, 2025 - CRITICAL FIX: ReportLab Import Correction
Description: Export service for generating PDF reports from fact-check results

LATEST HOTFIX (October 25, 2025 - 6:50 PM):
- FIXED: Corrected ReportLab import - 'colors' is a module, not an object
- CHANGED: from reportlab.lib.colors import colors → from reportlab.lib import colors
- REASON: ImportError: cannot import name 'colors' from 'reportlab.lib.colors'
- PRESERVED: All existing functionality (DO NO HARM ✓)

PREVIOUS CHANGES (October 25, 2025):
- FIXED: Proper ReportLab error handling
- IMPROVED: Better logging for debugging PDF issues
- ADDED: JSON and TXT export support

PURPOSE:
This file generates professional PDF reports for transcript fact-checking results.
It creates downloadable PDFs with:
- Trust score prominently displayed
- Content summary
- All claims with their verdicts
- Detailed fact-check results
- Sources and evidence

KEY FEATURES:
- Method: export_pdf(results, job_id) - main entry point
- Method: export_json(results, job_id) - JSON export
- Method: export_txt(results, job_id) - Text export
- Returns: File path to generated file
- Professional formatting with color-coded verdicts
- Complete claim-by-claim breakdown
- Automatic fallback if ReportLab unavailable

Deploy to: services/export_service.py

This is a COMPLETE file ready for deployment.
I did no harm and this file is not truncated.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Try to import ReportLab with detailed error logging
REPORTLAB_AVAILABLE = False
REPORTLAB_ERROR = None

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors  # ✅ FIXED: Import the module itself
    from reportlab.lib.colors import HexColor  # ✅ CORRECT: Import specific classes
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
    logger.info("[ExportService] ✓ ReportLab imported successfully")
except ImportError as e:
    REPORTLAB_ERROR = str(e)
    logger.error(f"[ExportService] ✗ ReportLab import failed: {e}")
    logger.error(f"[ExportService] Python version: {sys.version}")
    logger.error(f"[ExportService] Python path: {sys.path}")
except Exception as e:
    REPORTLAB_ERROR = str(e)
    logger.error(f"[ExportService] ✗ Unexpected error importing ReportLab: {e}")


class ExportService:
    """Export service for generating reports in multiple formats"""
    
    def __init__(self):
        """Initialize export service"""
        # Create exports directory if it doesn't exist
        self.exports_dir = 'exports'
        if not os.path.exists(self.exports_dir):
            try:
                os.makedirs(self.exports_dir)
                logger.info(f"[ExportService] Created exports directory: {self.exports_dir}")
            except Exception as e:
                logger.error(f"[ExportService] Failed to create exports directory: {e}")
        
        self.pdf_available = REPORTLAB_AVAILABLE
        
        if self.pdf_available:
            logger.info("[ExportService] ✓ Initialized - PDF export ENABLED")
        else:
            logger.warning(f"[ExportService] ⚠️  Initialized - PDF export DISABLED (Error: {REPORTLAB_ERROR})")
            logger.warning("[ExportService] To enable PDF export:")
            logger.warning("[ExportService] 1. Add 'reportlab==4.0.7' to requirements.txt")
            logger.warning("[ExportService] 2. Run: pip install reportlab")
            logger.warning("[ExportService] 3. Restart the application")
    
    def export_pdf(self, results: Dict[str, Any], job_id: str) -> str:
        """
        Export results to PDF format - main entry point
        
        Args:
            results (dict): Analysis results from transcript_routes
            job_id (str): Job ID for filename
            
        Returns:
            str: File path to generated PDF
            
        Raises:
            Exception: If PDF generation fails
        """
        if not self.pdf_available:
            error_msg = f"PDF export not available - ReportLab not installed. "
            error_msg += f"Error: {REPORTLAB_ERROR}. "
            error_msg += "Please install reportlab: pip install reportlab"
            logger.error(f"[ExportService] {error_msg}")
            raise Exception(error_msg)
        
        logger.info(f"[ExportService] Generating PDF for job {job_id}")
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"transcript_factcheck_{job_id[:8]}_{timestamp}.pdf"
        filepath = os.path.join(self.exports_dir, filename)
        
        # Generate PDF
        try:
            self._generate_pdf(results, filepath)
            logger.info(f"[ExportService] ✓ PDF generated: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"[ExportService] PDF generation failed: {e}", exc_info=True)
            raise
    
    def export_json(self, results: Dict[str, Any], job_id: str) -> str:
        """
        Export results to JSON format
        
        Args:
            results (dict): Analysis results
            job_id (str): Job ID for filename
            
        Returns:
            str: File path to generated JSON file
        """
        logger.info(f"[ExportService] Generating JSON for job {job_id}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"transcript_factcheck_{job_id[:8]}_{timestamp}.json"
        filepath = os.path.join(self.exports_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[ExportService] ✓ JSON generated: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"[ExportService] JSON generation failed: {e}", exc_info=True)
            raise
    
    def export_txt(self, results: Dict[str, Any], job_id: str) -> str:
        """
        Export results to plain text format
        
        Args:
            results (dict): Analysis results
            job_id (str): Job ID for filename
            
        Returns:
            str: File path to generated text file
        """
        logger.info(f"[ExportService] Generating TXT for job {job_id}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"transcript_factcheck_{job_id[:8]}_{timestamp}.txt"
        filepath = os.path.join(self.exports_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("TRANSCRIPT FACT-CHECK REPORT\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n")
                f.write(f"Job ID: {job_id}\n\n")
                
                # Summary
                f.write("-" * 80 + "\n")
                f.write("SUMMARY\n")
                f.write("-" * 80 + "\n")
                f.write(f"{results.get('summary', 'No summary available')}\n\n")
                
                # Credibility Score
                score_info = results.get('credibility_score', {})
                f.write("-" * 80 + "\n")
                f.write("CREDIBILITY SCORE\n")
                f.write("-" * 80 + "\n")
                f.write(f"Score: {score_info.get('score', 0)}/100\n")
                f.write(f"Label: {score_info.get('label', 'Unknown')}\n")
                f.write(f"Total Claims Analyzed: {score_info.get('total_claims', 0)}\n\n")
                
                # Fact Checks
                fact_checks = results.get('fact_checks', [])
                if fact_checks:
                    f.write("=" * 80 + "\n")
                    f.write("DETAILED FACT CHECKS\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for i, fc in enumerate(fact_checks, 1):
                        f.write(f"CLAIM #{i}\n")
                        f.write("-" * 80 + "\n")
                        f.write(f"Claim: {fc.get('claim', 'N/A')}\n")
                        f.write(f"Speaker: {fc.get('speaker', 'Unknown')}\n")
                        f.write(f"Verdict: {fc.get('verdict_label', fc.get('verdict', 'N/A')).upper()}\n")
                        f.write(f"Confidence: {fc.get('confidence', 0)}%\n\n")
                        f.write(f"Explanation:\n{fc.get('explanation', 'No explanation provided')}\n\n")
                        
                        sources = fc.get('sources', [])
                        if sources:
                            f.write(f"Sources: {', '.join(sources)}\n")
                        
                        f.write("\n" + "=" * 80 + "\n\n")
                
                # Speakers
                speakers = results.get('speakers', [])
                if speakers:
                    f.write("-" * 80 + "\n")
                    f.write("SPEAKERS\n")
                    f.write("-" * 80 + "\n")
                    f.write(", ".join(speakers) + "\n\n")
                
                # Topics
                topics = results.get('topics', [])
                if topics:
                    f.write("-" * 80 + "\n")
                    f.write("TOPICS\n")
                    f.write("-" * 80 + "\n")
                    f.write(", ".join(topics) + "\n\n")
            
            logger.info(f"[ExportService] ✓ TXT generated: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"[ExportService] TXT generation failed: {e}", exc_info=True)
            raise
    
    def _generate_pdf(self, results: Dict[str, Any], filepath: str):
        """Generate the actual PDF document"""
        # Create document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        self._add_custom_styles(styles)
        
        # Build content
        story = []
        
        # Title
        title = Paragraph("Transcript Fact-Check Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Metadata
        metadata_text = f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>"
        metadata_text += f"Job ID: {results.get('instance_id', 'N/A')}"
        metadata = Paragraph(metadata_text, styles['Normal'])
        story.append(metadata)
        story.append(Spacer(1, 0.5*inch))
        
        # Credibility Score (prominent)
        score_info = results.get('credibility_score', {})
        score = score_info.get('score', 0)
        label = score_info.get('label', 'Unknown')
        
        score_text = f"<font size=16><b>Credibility Score: {score}/100</b></font><br/>"
        score_text += f"<font size=12>{label}</font>"
        score_para = Paragraph(score_text, styles['BodyText'])
        story.append(score_para)
        story.append(Spacer(1, 0.4*inch))
        
        # Summary
        story.append(Paragraph("<b>Summary</b>", styles['Heading2']))
        summary_text = results.get('summary', 'No summary available')
        story.append(Paragraph(summary_text, styles['BodyText']))
        story.append(Spacer(1, 0.3*inch))
        
        # Speakers and Topics
        speakers = results.get('speakers', [])
        topics = results.get('topics', [])
        
        if speakers:
            speakers_text = f"<b>Speakers:</b> {', '.join(speakers)}"
            story.append(Paragraph(speakers_text, styles['Normal']))
        
        if topics:
            topics_text = f"<b>Topics:</b> {', '.join(topics)}"
            story.append(Paragraph(topics_text, styles['Normal']))
        
        story.append(Spacer(1, 0.5*inch))
        story.append(PageBreak())
        
        # Fact Checks
        fact_checks = results.get('fact_checks', [])
        if fact_checks:
            story.append(Paragraph("<b>Detailed Fact Checks</b>", styles['Heading1']))
            story.append(Spacer(1, 0.2*inch))
            
            for i, fc in enumerate(fact_checks, 1):
                # Claim number
                claim_header = f"<b>Claim #{i}</b>"
                story.append(Paragraph(claim_header, styles['Heading3']))
                story.append(Spacer(1, 0.1*inch))
                
                # Claim text
                claim_text = self._escape_html(fc.get('claim', 'N/A'))
                story.append(Paragraph(f"<i>\"{claim_text}\"</i>", styles['BodyText']))
                story.append(Spacer(1, 0.1*inch))
                
                # Speaker
                speaker = fc.get('speaker', 'Unknown')
                story.append(Paragraph(f"<b>Speaker:</b> {speaker}", styles['Normal']))
                
                # Verdict
                verdict = fc.get('verdict_label', fc.get('verdict', 'N/A')).upper()
                verdict_color = self._get_verdict_color(fc.get('verdict', ''))
                verdict_text = f"<b>Verdict:</b> <font color='{verdict_color}'><b>{verdict}</b></font>"
                story.append(Paragraph(verdict_text, styles['Normal']))
                
                # Confidence
                confidence = fc.get('confidence', 0)
                story.append(Paragraph(f"<b>Confidence:</b> {confidence}%", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
                
                # Explanation
                explanation = self._escape_html(fc.get('explanation', 'No explanation provided'))
                story.append(Paragraph(f"<b>Explanation:</b>", styles['Normal']))
                story.append(Paragraph(explanation, styles['BodyText']))
                story.append(Spacer(1, 0.1*inch))
                
                # Sources
                sources = fc.get('sources', [])
                if sources:
                    sources_text = f"<b>Sources:</b> {', '.join(sources)}"
                    story.append(Paragraph(sources_text, styles['Normal']))
                
                story.append(Spacer(1, 0.3*inch))
                
                # Page break every 3 claims
                if i % 3 == 0 and i < len(fact_checks):
                    story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
    
    def _add_custom_styles(self, styles):
        """Add custom paragraph styles"""
        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=HexColor('#1f2937'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))
    
    def _get_verdict_color(self, verdict: str) -> str:
        """Get color code for verdict"""
        verdict_lower = verdict.lower()
        
        verdict_colors = {
            'true': '#10b981',
            'mostly_true': '#34d399',
            'partially_true': '#fbbf24',
            'misleading': '#fb923c',
            'mostly_false': '#f87171',
            'false': '#ef4444',
            'unverifiable': '#9ca3af',
            'opinion': '#6366f1'
        }
        
        return verdict_colors.get(verdict_lower, '#6b7280')
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        if not text:
            return ''
        
        return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


# I did no harm and this file is not truncated
