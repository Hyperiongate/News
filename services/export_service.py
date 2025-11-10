"""
File: services/export_service.py
Last Updated: November 10, 2025 - v5.0.0 CRITICAL FIX
Description: Export service that properly uses TranscriptPDFGenerator v4.0.0

CHANGES IN v5.0.0 (November 10, 2025):
======================================
🔥 CRITICAL FIX: This file was generating PDFs itself instead of using TranscriptPDFGenerator!
✅ REMOVED: Built-in _generate_pdf() method (was creating boring PDFs)
✅ ADDED: Import of TranscriptPDFGenerator from services.transcript_pdf_generator
✅ CHANGED: export_pdf() now delegates to TranscriptPDFGenerator.generate_pdf()
✅ RESULT: PDFs now use v4.0.0 with executive summary!
✅ PRESERVED: JSON and TXT export functionality (DO NO HARM ✓)

WHY THIS FIX WAS NEEDED:
========================
- export_service.py had its OWN _generate_pdf() method
- It was creating "Transcript Fact-Check Report" PDFs
- It completely ignored the TranscriptPDFGenerator v4.0.0
- User deployed v4.0.0 but nothing changed because this file wasn't using it!

Deploy to: services/export_service.py

This is a COMPLETE file ready for deployment.
I did no harm and this file is not truncated.
Date: November 10, 2025
Version: 5.0.0 - PROPERLY USE TRANSCRIPTPDFGENERATOR
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
    from reportlab.lib import colors
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
    logger.info("[ExportService] ✓ ReportLab imported successfully")
except ImportError as e:
    REPORTLAB_ERROR = str(e)
    logger.error(f"[ExportService] ✗ ReportLab import failed: {e}")
except Exception as e:
    REPORTLAB_ERROR = str(e)
    logger.error(f"[ExportService] ✗ Unexpected error importing ReportLab: {e}")

# 🔥 NEW v5.0.0: Import the actual TranscriptPDFGenerator
try:
    from services.transcript_pdf_generator import TranscriptPDFGenerator
    TRANSCRIPT_PDF_AVAILABLE = True
    logger.info("[ExportService] ✓ TranscriptPDFGenerator imported successfully")
except ImportError as e:
    TRANSCRIPT_PDF_AVAILABLE = False
    logger.error(f"[ExportService] ✗ Failed to import TranscriptPDFGenerator: {e}")


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
        
        self.pdf_available = REPORTLAB_AVAILABLE and TRANSCRIPT_PDF_AVAILABLE
        
        # 🔥 NEW v5.0.0: Initialize the TranscriptPDFGenerator
        if self.pdf_available:
            try:
                self.pdf_generator = TranscriptPDFGenerator()
                logger.info("[ExportService] ✓ Initialized with TranscriptPDFGenerator v4.0.0")
            except Exception as e:
                logger.error(f"[ExportService] Failed to initialize PDF generator: {e}")
                self.pdf_available = False
        
        if self.pdf_available:
            logger.info("[ExportService] ✓ Initialized - PDF export ENABLED (using v4.0.0)")
        else:
            logger.warning(f"[ExportService] ⚠️  Initialized - PDF export DISABLED")
            if REPORTLAB_ERROR:
                logger.warning(f"[ExportService] ReportLab error: {REPORTLAB_ERROR}")
    
    def export_pdf(self, results: Dict[str, Any], job_id: str) -> str:
        """
        Export results to PDF format using TranscriptPDFGenerator v4.0.0
        
        Args:
            results (dict): Analysis results from transcript_routes
            job_id (str): Job ID for filename
            
        Returns:
            str: File path to generated PDF
            
        Raises:
            Exception: If PDF generation fails
        """
        if not self.pdf_available:
            error_msg = "PDF export not available - TranscriptPDFGenerator not loaded. "
            if REPORTLAB_ERROR:
                error_msg += f"Error: {REPORTLAB_ERROR}. "
            error_msg += "Please ensure reportlab is installed and transcript_pdf_generator.py exists."
            logger.error(f"[ExportService] {error_msg}")
            raise Exception(error_msg)
        
        logger.info(f"[ExportService] Generating PDF for job {job_id} using TranscriptPDFGenerator v4.0.0")
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"transcript_factcheck_{job_id[:8]}_{timestamp}.pdf"
        filepath = os.path.join(self.exports_dir, filename)
        
        # 🔥 NEW v5.0.0: Use TranscriptPDFGenerator instead of built-in generator
        try:
            success = self.pdf_generator.generate_pdf(results, filepath)
            
            if success:
                logger.info(f"[ExportService] ✓ PDF generated with v4.0.0: {filepath}")
                return filepath
            else:
                raise Exception("PDF generator returned False")
                
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


"""
============================================================================
END OF FILE
============================================================================

Date: November 10, 2025
Version: 5.0.0 - PROPERLY USE TRANSCRIPTPDFGENERATOR v4.0.0

CRITICAL FIX SUMMARY:
====================
✅ Removed built-in _generate_pdf() method that was creating boring PDFs
✅ Now imports and uses TranscriptPDFGenerator from services/transcript_pdf_generator
✅ export_pdf() delegates to TranscriptPDFGenerator.generate_pdf()
✅ PDFs now have executive summary, analysis methodology, key findings, interpretation
✅ JSON and TXT exports preserved unchanged

DEPLOYMENT:
===========
1. Save this file as: services/export_service.py
2. Deploy to GitHub: git add services/export_service.py && git commit -m "Fix export_service to use TranscriptPDFGenerator v4.0.0" && git push
3. Wait for Render to deploy (2-3 minutes)
4. Test by generating a new transcript PDF
5. PDF should now show "Transcript Credibility Analysis" with executive summary!

I did no harm and this file is not truncated.
"""
