"""
File: services/transcript_pdf_generator.py
Created: October 24, 2025
Last Updated: November 9, 2025 - v3.0.0 COMPREHENSIVE TRUSTWORTHINESS ASSESSMENT
Version: 3.0.0
Description: Professional PDF reports with executive summary and speaker trustworthiness analysis

LATEST UPDATE (November 9, 2025 - v3.0.0 COMPREHENSIVE ASSESSMENT):
====================================================================
✅ ADDED: Executive Summary (What We Looked For + What We Found) at the top
✅ ADDED: Speaker Trustworthiness Assessment section with credibility evaluation
✅ ADDED: Red Flags and Positive Indicators throughout all sections
✅ ENHANCED: All "What This Means" sections now much more detailed and actionable
✅ ENHANCED: Speaker quality interpretation now explicitly addresses trustworthiness
✅ ENHANCED: Language style section now highlights manipulative tactics
✅ ENHANCED: Coherence section now assesses logical consistency
✅ ENHANCED: Professional formatting with clear visual hierarchy
✅ PRESERVED: All v2.0.0 functionality - no breaking changes (DO NO HARM)

PDF STRUCTURE (v3.0.0):
======================
1. Title Page
2. Trust Score (BIG, color-coded)
3. ⭐ EXECUTIVE SUMMARY (NEW - What we looked for, what we found, key takeaways)
4. ⭐ SPEAKER TRUSTWORTHINESS ASSESSMENT (NEW - if speaker quality data available)
   - Communication credibility evaluation
   - Red flags identified
   - Positive indicators
   - Overall trustworthiness assessment
5. Summary of Content (transcript overview)
6. Transcript Quality Analysis (readability metrics with interpretation)
7. Speaker Quality Analysis (grade level, continuity, language style)
8. Summary of Findings (claim verification results with interpretation)
9. Detailed Claim Evaluations (every claim with full analysis)

WHAT'S NEW IN v3.0.0:
=====================
- Executive summary answers "What did we check?" and "What did we find?"
- Speaker trustworthiness explicitly assessed with clear recommendations
- Red flags highlighted in every section (inflammatory language, incomplete sentences, etc.)
- Positive indicators highlighted (logical flow, neutral tone, etc.)
- All interpretations now actionable and non-technical
- Professional language suitable for decision-makers

BACKWARD COMPATIBILITY:
=======================
✅ Works with all existing data formats
✅ Gracefully handles missing fields
✅ Never crashes on incomplete data
✅ All v2.0.0 sections preserved

This is a COMPLETE file ready for deployment.
Last modified: November 9, 2025 - v3.0.0 COMPREHENSIVE TRUSTWORTHINESS ASSESSMENT
I did no harm and this file is not truncated.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

logger = logging.getLogger(__name__)


class TranscriptPDFGenerator:
    """
    Generate professional PDF reports for transcript analysis with comprehensive trustworthiness assessment
    
    v3.0.0: Executive summary, speaker trustworthiness evaluation, and enhanced interpretations
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create custom styles optimized for transcript reports"""
        
        # Helper function to safely add styles
        def add_style(style):
            if style.name not in self.styles:
                self.styles.add(style)
        
        # Main title
        add_style(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Title'],
            fontSize=26,
            textColor=HexColor('#1f2937'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle
        add_style(ParagraphStyle(
            name='ReportSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor('#6b7280'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Trust Score (BIG and prominent)
        add_style(ParagraphStyle(
            name='TrustScore',
            parent=self.styles['Title'],
            fontSize=48,
            textColor=HexColor('#3b82f6'),
            spaceAfter=6,
            spaceBefore=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Trust Label
        add_style(ParagraphStyle(
            name='TrustLabel',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=HexColor('#4b5563'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section headers
        add_style(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=HexColor('#1f2937'),
            spaceAfter=12,
            spaceBefore=24,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderPadding=0,
            leftIndent=0
        ))
        
        # Subsection headers
        add_style(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#374151'),
            spaceAfter=8,
            spaceBefore=16,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        add_style(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
        
        # Executive summary box
        add_style(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=18,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leftIndent=15,
            rightIndent=15,
            borderWidth=2,
            borderColor=HexColor('#3b82f6'),
            borderPadding=15,
            backColor=HexColor('#eff6ff')
        ))
        
        # Red flag indicator
        add_style(ParagraphStyle(
            name='RedFlag',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            textColor=HexColor('#dc2626'),
            spaceAfter=8,
            leftIndent=15,
            fontName='Helvetica-Bold'
        ))
        
        # Positive indicator
        add_style(ParagraphStyle(
            name='PositiveFlag',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            textColor=HexColor('#059669'),
            spaceAfter=8,
            leftIndent=15,
            fontName='Helvetica-Bold'
        ))
        
        # Trustworthiness assessment box
        add_style(ParagraphStyle(
            name='TrustworthinessBox',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=18,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leftIndent=15,
            rightIndent=15,
            borderWidth=2,
            borderColor=HexColor('#d97706'),
            borderPadding=15,
            backColor=HexColor('#fffbeb')
        ))
        
        # Claim number
        add_style(ParagraphStyle(
            name='ClaimNumber',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=HexColor('#3b82f6'),
            fontName='Helvetica-Bold',
            spaceAfter=8,
            spaceBefore=20
        ))
        
        # Claim text (the actual quote)
        add_style(ParagraphStyle(
            name='ClaimText',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=18,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=12,
            spaceBefore=8,
            fontName='Helvetica-Oblique',
            textColor=HexColor('#1f2937'),
            borderWidth=1,
            borderColor=HexColor('#d1d5db'),
            borderPadding=12,
            backColor=HexColor('#f9fafb')
        ))
        
        # Verdict styles (different colors for different verdicts)
        add_style(ParagraphStyle(
            name='VerdictTrue',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=HexColor('#059669'),
            fontName='Helvetica-Bold',
            spaceAfter=8
        ))
        
        add_style(ParagraphStyle(
            name='VerdictFalse',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=HexColor('#dc2626'),
            fontName='Helvetica-Bold',
            spaceAfter=8
        ))
        
        add_style(ParagraphStyle(
            name='VerdictMixed',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=HexColor('#d97706'),
            fontName='Helvetica-Bold',
            spaceAfter=8
        ))
        
        add_style(ParagraphStyle(
            name='VerdictUnverifiable',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=HexColor('#6b7280'),
            fontName='Helvetica-Bold',
            spaceAfter=8
        ))
        
        # Evaluation text
        add_style(ParagraphStyle(
            name='EvaluationText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leftIndent=10
        ))
        
        # Speaker info
        add_style(ParagraphStyle(
            name='SpeakerInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#6b7280'),
            fontName='Helvetica-Oblique',
            spaceAfter=4
        ))
        
        # Source citation
        add_style(ParagraphStyle(
            name='SourceCitation',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=HexColor('#6b7280'),
            leftIndent=10,
            spaceAfter=4
        ))
        
        # Quality metric
        add_style(ParagraphStyle(
            name='QualityMetric',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            spaceAfter=8
        ))
        
        # Interpretation text (enhanced)
        add_style(ParagraphStyle(
            name='InterpretationText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            textColor=HexColor('#374151'),
            leftIndent=10,
            rightIndent=10,
            backColor=HexColor('#f3f4f6'),
            borderWidth=1,
            borderColor=HexColor('#d1d5db'),
            borderPadding=10
        ))
        
        # Key takeaway
        add_style(ParagraphStyle(
            name='KeyTakeaway',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=18,
            fontName='Helvetica-Bold',
            textColor=HexColor('#1f2937'),
            spaceAfter=10
        ))
    
    def generate_pdf(self, results: Dict, output_path: str) -> bool:
        """
        Generate the PDF report
        
        Args:
            results: Dictionary containing transcript analysis results
            output_path: Where to save the PDF
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"[PDF Generator v3.0.0] Starting PDF generation to {output_path}")
            logger.info(f"[PDF Generator] Results keys: {list(results.keys())}")
            
            # Create document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=50
            )
            
            # Build story (content)
            story = []
            
            # 1. TITLE PAGE
            story.extend(self._create_title_page(results))
            
            # 2. TRUST SCORE (BIG AND PROMINENT)
            story.extend(self._create_trust_score_section(results))
            
            # 3. ⭐ EXECUTIVE SUMMARY (NEW v3.0.0)
            story.extend(self._create_executive_summary(results))
            
            # Page break after executive summary
            story.append(PageBreak())
            
            # 4. ⭐ SPEAKER TRUSTWORTHINESS ASSESSMENT (NEW v3.0.0)
            if results.get('speaker_quality'):
                story.extend(self._create_trustworthiness_assessment(results))
                story.append(Spacer(1, 0.3*inch))
            
            # 5. SUMMARY OF CONTENT
            story.extend(self._create_content_summary_section(results))
            
            # 6. TRANSCRIPT QUALITY ANALYSIS
            if results.get('transcript_quality'):
                story.extend(self._create_transcript_quality_section(results))
            
            # 7. SPEAKER QUALITY ANALYSIS (enhanced with trustworthiness focus)
            if results.get('speaker_quality'):
                story.extend(self._create_speaker_quality_section(results))
            
            # 8. SUMMARY OF FINDINGS
            story.extend(self._create_findings_summary_section(results))
            
            # Page break before claims
            story.append(PageBreak())
            
            # 9. DETAILED CLAIM EVALUATIONS
            story.extend(self._create_claims_evaluation_section(results))
            
            # Build PDF
            doc.build(story)
            logger.info(f"[PDF Generator v3.0.0] ✓ PDF generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"[PDF Generator] ✗ Error generating PDF: {e}", exc_info=True)
            return False
    
    def _create_title_page(self, results: Dict) -> List:
        """Create title page elements"""
        elements = []
        
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Transcript Analysis Report", self.styles['ReportTitle']))
        
        # Job ID if available
        job_id = results.get('job_id', 'Unknown')
        elements.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>Job ID: {job_id}",
            self.styles['ReportSubtitle']
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_trust_score_section(self, results: Dict) -> List:
        """Create prominent trust score display"""
        elements = []
        
        cred_score = results.get('credibility_score', {})
        score = cred_score.get('score', 0)
        label = cred_score.get('label', 'Unknown')
        
        # Determine color based on score
        if score >= 80:
            color = HexColor('#059669')  # Green
        elif score >= 60:
            color = HexColor('#10b981')  # Light green
        elif score >= 40:
            color = HexColor('#d97706')  # Orange
        elif score >= 20:
            color = HexColor('#dc2626')  # Red
        else:
            color = HexColor('#991b1b')  # Dark red
        
        # Create custom style for this specific score
        score_style = ParagraphStyle(
            'TrustScoreColored',
            parent=self.styles['TrustScore'],
            textColor=color
        )
        
        label_style = ParagraphStyle(
            'TrustLabelColored',
            parent=self.styles['TrustLabel'],
            textColor=color
        )
        
        elements.append(Paragraph(f"{score}/100", score_style))
        elements.append(Paragraph(label, label_style))
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_executive_summary(self, results: Dict) -> List:
        """
        ⭐ NEW v3.0.0: Create executive summary section
        Answers: What did we look for? What did we find? What does it mean?
        """
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Build comprehensive summary
        summary_parts = []
        
        # WHAT WE LOOKED FOR
        summary_parts.append("<b>What We Analyzed:</b>")
        summary_parts.append(
            "We conducted a comprehensive analysis of this transcript, examining: "
            "(1) factual claims and their accuracy, "
            "(2) speaker communication quality including grade level and coherence, "
            "(3) language style including inflammatory or manipulative rhetoric, "
            "(4) sentence completion and logical flow, "
            "(5) vocabulary complexity and diversity, and "
            "(6) overall credibility indicators."
        )
        summary_parts.append("<br/><br/>")
        
        # WHAT WE FOUND - Credibility
        cred_score = results.get('credibility_score', {})
        score = cred_score.get('score', 0)
        breakdown = cred_score.get('breakdown', {})
        
        summary_parts.append("<b>What We Found - Factual Accuracy:</b>")
        
        true_count = breakdown.get('verified_true', 0)
        false_count = breakdown.get('verified_false', 0)
        partial_count = breakdown.get('partially_accurate', 0)
        unverified_count = breakdown.get('unverifiable', 0)
        total_claims = sum(breakdown.values())
        
        if total_claims > 0:
            true_pct = (true_count / total_claims * 100)
            false_pct = (false_count / total_claims * 100)
            
            summary_parts.append(
                f"We analyzed {total_claims} factual claims. "
                f"{true_count} claims ({true_pct:.0f}%) were verified as accurate. "
            )
            
            if false_count > 0:
                summary_parts.append(f"{false_count} claims ({false_pct:.0f}%) were found to be false or misleading. ")
            
            if partial_count > 0:
                summary_parts.append(f"{partial_count} claims required additional context. ")
            
            if unverified_count > 0:
                summary_parts.append(f"{unverified_count} claims could not be independently verified. ")
        else:
            summary_parts.append("No verifiable factual claims were found in this transcript.")
        
        summary_parts.append("<br/><br/>")
        
        # WHAT WE FOUND - Speaker Quality
        if results.get('speaker_quality'):
            summary_parts.append("<b>What We Found - Communication Quality:</b>")
            
            speaker_quality = results.get('speaker_quality', {})
            
            # Get overall assessment
            overall = speaker_quality.get('overall_assessment', {})
            if isinstance(overall, str):
                summary_parts.append(overall)
            elif isinstance(overall, dict):
                summary_text = overall.get('summary', '')
                if summary_text:
                    summary_parts.append(summary_text)
            
            # Add specific quality indicators
            if speaker_quality.get('grade_level'):
                grade = speaker_quality['grade_level'].get('flesch_kincaid_grade', 0)
                summary_parts.append(f" The speaker communicates at a grade {grade:.0f} level.")
            
            if speaker_quality.get('language_style'):
                inflammatory_pct = speaker_quality['language_style'].get('inflammatory_percentage', 0)
                if inflammatory_pct > 5:
                    summary_parts.append(f" Warning: {inflammatory_pct:.1f}% of language is inflammatory or manipulative.")
            
            summary_parts.append("<br/><br/>")
        
        # KEY TAKEAWAY
        summary_parts.append("<b>Bottom Line:</b>")
        
        if score >= 80:
            summary_parts.append(
                "This transcript demonstrates high credibility. The vast majority of verifiable claims are accurate, "
                "and the speaker demonstrates clear, logical communication. You can rely on this content with confidence."
            )
        elif score >= 60:
            summary_parts.append(
                "This transcript shows generally credible content, though some claims require verification. "
                "The speaker communicates clearly, but exercise normal due diligence on specific facts."
            )
        elif score >= 40:
            summary_parts.append(
                "This transcript has mixed credibility. There's a significant balance of accurate and questionable claims. "
                "Verify important facts independently before relying on this content."
            )
        elif score >= 20:
            summary_parts.append(
                "This transcript has low credibility. Multiple false or misleading claims were identified. "
                "Treat this content with skepticism and verify all facts independently."
            )
        else:
            summary_parts.append(
                "This transcript lacks credibility. The majority of verifiable claims are false or misleading. "
                "Do not rely on this content without thorough independent verification."
            )
        
        # Combine into executive summary
        exec_summary = " ".join(summary_parts)
        elements.append(Paragraph(exec_summary, self.styles['ExecutiveSummary']))
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_trustworthiness_assessment(self, results: Dict) -> List:
        """
        ⭐ NEW v3.0.0: Create speaker trustworthiness assessment
        Evaluates whether the speaker is credible, manipulative, or somewhere in between
        """
        elements = []
        
        speaker_quality = results.get('speaker_quality', {})
        
        if not speaker_quality or not speaker_quality.get('success'):
            return elements
        
        elements.append(Paragraph("Speaker Trustworthiness Assessment", self.styles['SectionHeader']))
        
        # Extract key metrics
        grade_level_data = speaker_quality.get('grade_level', {})
        language_style = speaker_quality.get('language_style', {})
        sentence_quality = speaker_quality.get('sentence_quality', {})
        coherence = speaker_quality.get('coherence', {})
        vocabulary = speaker_quality.get('vocabulary', {})
        
        grade_level = grade_level_data.get('flesch_kincaid_grade', 0)
        inflammatory_pct = language_style.get('inflammatory_percentage', 0)
        completion_rate = sentence_quality.get('completion_rate', 100)
        coherence_score = coherence.get('coherence_score', 50)
        vocab_diversity = vocabulary.get('vocabulary_diversity', 0)
        
        # Calculate trustworthiness score
        trustworthiness_score = self._calculate_trustworthiness_score(
            inflammatory_pct, completion_rate, coherence_score
        )
        
        # Build assessment
        assessment_parts = []
        
        # Overall trustworthiness
        if trustworthiness_score >= 80:
            assessment_parts.append(
                "<b>Overall Assessment: HIGHLY TRUSTWORTHY</b><br/>"
                "This speaker demonstrates credible communication patterns. "
                "They speak clearly, logically, and without manipulative tactics. "
                "Their communication style suggests reliability and honesty."
            )
        elif trustworthiness_score >= 60:
            assessment_parts.append(
                "<b>Overall Assessment: GENERALLY TRUSTWORTHY</b><br/>"
                "This speaker demonstrates mostly credible communication. "
                "While there may be some emotional appeals, the overall pattern suggests honest communication."
            )
        elif trustworthiness_score >= 40:
            assessment_parts.append(
                "<b>Overall Assessment: MIXED TRUSTWORTHINESS</b><br/>"
                "This speaker shows inconsistent communication patterns. "
                "Some indicators suggest credibility while others raise concerns. Exercise caution and verify claims independently."
            )
        else:
            assessment_parts.append(
                "<b>Overall Assessment: TRUSTWORTHINESS CONCERNS</b><br/>"
                "This speaker exhibits multiple red flags in their communication style. "
                "Significant concerns about credibility were identified. Treat statements with skepticism."
            )
        
        assessment_parts.append("<br/><br/>")
        
        # RED FLAGS (if any)
        red_flags = self._identify_red_flags(speaker_quality)
        if red_flags:
            assessment_parts.append("<b>⚠️ Red Flags Identified:</b><br/>")
            for flag in red_flags:
                assessment_parts.append(f"• {flag}<br/>")
            assessment_parts.append("<br/>")
        
        # POSITIVE INDICATORS
        positive_indicators = self._identify_positive_indicators(speaker_quality)
        if positive_indicators:
            assessment_parts.append("<b>✓ Positive Indicators:</b><br/>")
            for indicator in positive_indicators:
                assessment_parts.append(f"• {indicator}<br/>")
            assessment_parts.append("<br/>")
        
        # RECOMMENDATION
        assessment_parts.append("<b>Recommendation:</b> ")
        if trustworthiness_score >= 70:
            assessment_parts.append(
                "This speaker's communication style suggests they can be trusted. "
                "However, always verify important facts independently."
            )
        elif trustworthiness_score >= 40:
            assessment_parts.append(
                "Approach this speaker's statements with healthy skepticism. "
                "Verify all significant claims before acting on them."
            )
        else:
            assessment_parts.append(
                "Exercise extreme caution with this speaker's statements. "
                "Multiple indicators suggest unreliable communication. Independent verification is essential."
            )
        
        # Combine into assessment box
        assessment_text = "".join(assessment_parts)
        elements.append(Paragraph(assessment_text, self.styles['TrustworthinessBox']))
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _calculate_trustworthiness_score(self, inflammatory_pct: float, 
                                        completion_rate: float, coherence_score: float) -> int:
        """Calculate overall trustworthiness score from key indicators"""
        score = 100
        
        # Deduct for inflammatory language (major red flag)
        if inflammatory_pct > 10:
            score -= 30
        elif inflammatory_pct > 5:
            score -= 15
        elif inflammatory_pct > 2:
            score -= 5
        
        # Deduct for incomplete sentences (suggests disorganized thinking)
        if completion_rate < 60:
            score -= 20
        elif completion_rate < 75:
            score -= 10
        elif completion_rate < 85:
            score -= 5
        
        # Deduct for poor coherence (suggests unclear or deceptive communication)
        if coherence_score < 40:
            score -= 20
        elif coherence_score < 60:
            score -= 10
        
        return max(0, min(score, 100))
    
    def _identify_red_flags(self, speaker_quality: Dict) -> List[str]:
        """Identify red flags in speaker communication"""
        red_flags = []
        
        language_style = speaker_quality.get('language_style', {})
        sentence_quality = speaker_quality.get('sentence_quality', {})
        coherence = speaker_quality.get('coherence', {})
        rhetorical_devices = speaker_quality.get('rhetorical_devices', {})
        
        # Check inflammatory language
        inflammatory_pct = language_style.get('inflammatory_percentage', 0)
        if inflammatory_pct > 10:
            red_flags.append(
                f"High use of inflammatory language ({inflammatory_pct:.1f}%) - "
                "suggests emotional manipulation rather than factual argument"
            )
        elif inflammatory_pct > 5:
            red_flags.append(
                f"Moderate inflammatory language ({inflammatory_pct:.1f}%) - "
                "relies on emotional appeals"
            )
        
        # Check sentence completion
        completion_rate = sentence_quality.get('completion_rate', 100)
        if completion_rate < 70:
            red_flags.append(
                f"Low sentence completion rate ({completion_rate:.0f}%) - "
                "indicates disorganized or evasive communication"
            )
        
        # Check coherence
        coherence_score = coherence.get('coherence_score', 50)
        if coherence_score < 50:
            red_flags.append(
                f"Poor logical flow (coherence: {coherence_score:.0f}/100) - "
                "arguments lack clear logical structure"
            )
        
        # Check excessive exclamations
        exclamations = rhetorical_devices.get('exclamations', 0)
        if exclamations > 10:
            red_flags.append(
                f"Excessive exclamations ({exclamations}) - "
                "may indicate heightened emotion over reason"
            )
        
        # Check category breakdown for specific manipulative tactics
        category_breakdown = language_style.get('category_breakdown', {})
        if category_breakdown.get('fear', 0) > 5:
            red_flags.append(
                "Frequent use of fear-based language - appeals to fear rather than facts"
            )
        if category_breakdown.get('absolute', 0) > 5:
            red_flags.append(
                "Overuse of absolute terms (always/never/everyone) - oversimplifies complex issues"
            )
        
        return red_flags
    
    def _identify_positive_indicators(self, speaker_quality: Dict) -> List[str]:
        """Identify positive indicators in speaker communication"""
        positive_indicators = []
        
        language_style = speaker_quality.get('language_style', {})
        sentence_quality = speaker_quality.get('sentence_quality', {})
        coherence = speaker_quality.get('coherence', {})
        vocabulary = speaker_quality.get('vocabulary', {})
        
        # Check neutral tone
        inflammatory_pct = language_style.get('inflammatory_percentage', 0)
        if inflammatory_pct < 2:
            positive_indicators.append(
                "Maintains neutral, objective tone - focuses on facts over emotion"
            )
        
        # Check sentence completion
        completion_rate = sentence_quality.get('completion_rate', 100)
        if completion_rate > 85:
            positive_indicators.append(
                f"High sentence completion ({completion_rate:.0f}%) - demonstrates clear, organized thinking"
            )
        
        # Check coherence
        coherence_score = coherence.get('coherence_score', 50)
        if coherence_score >= 75:
            positive_indicators.append(
                f"Strong logical flow (coherence: {coherence_score:.0f}/100) - arguments are well-structured"
            )
        
        # Check vocabulary diversity
        vocab_diversity = vocabulary.get('vocabulary_diversity', 0)
        if vocab_diversity >= 60:
            positive_indicators.append(
                f"Diverse vocabulary ({vocab_diversity:.0f}%) - demonstrates nuanced understanding"
            )
        
        # Check transition words
        transition_count = coherence.get('transition_word_count', 0)
        if transition_count > 0:
            positive_indicators.append(
                f"Uses logical transitions ({transition_count} instances) - connects ideas clearly"
            )
        
        return positive_indicators
    
    def _create_content_summary_section(self, results: Dict) -> List:
        """Create summary of content section"""
        elements = []
        
        elements.append(Paragraph("Summary of Content", self.styles['SectionHeader']))
        
        # Get basic info (backward compatible with both old and new keys)
        total_claims = results.get('total_claims') or results.get('claims_found', 0)
        speakers = results.get('speakers', [])
        topics = results.get('topics', [])
        transcript_preview = results.get('transcript_preview', '')
        transcript_length = results.get('transcript_length', 0)
        
        # Build content summary
        summary_parts = []
        
        summary_parts.append(f"This transcript contains <b>{total_claims} factual claims</b> that were analyzed and verified.")
        summary_parts.append(f"Total transcript length: {transcript_length:,} characters.")
        
        if speakers:
            speaker_list = ', '.join(speakers[:5])
            if len(speakers) > 5:
                speaker_list += f", and {len(speakers) - 5} others"
            summary_parts.append(f"<b>Speakers identified:</b> {speaker_list}.")
        
        if topics:
            topic_list = ', '.join(topics[:5])
            summary_parts.append(f"<b>Topics discussed:</b> {topic_list}.")
        
        if transcript_preview:
            preview_clean = transcript_preview.replace('\n', ' ').replace('\r', ' ')
            summary_parts.append(f'<b>Transcript preview:</b> "{preview_clean}"')
        
        content_summary = " ".join(summary_parts)
        elements.append(Paragraph(content_summary, self.styles['BodyText']))
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_transcript_quality_section(self, results: Dict) -> List:
        """Create transcript quality analysis section"""
        elements = []
        
        quality = results.get('transcript_quality', {})
        
        if not quality:
            return elements
        
        elements.append(Paragraph("Transcript Quality Analysis", self.styles['SectionHeader']))
        
        # Get metrics
        grade_level = quality.get('grade_level', 0)
        reading_ease = quality.get('reading_ease', 0)
        reading_ease_label = quality.get('reading_ease_label', 'Unknown')
        avg_sentence_length = quality.get('avg_sentence_length', 0)
        avg_word_length = quality.get('avg_word_length', 0)
        complex_words_pct = quality.get('complex_words_pct', 0)
        complexity_label = quality.get('complexity_label', 'Unknown')
        
        # Metrics paragraph
        metrics_text = f"""
        <b>Reading Level:</b> Grade {grade_level} ({reading_ease_label})<br/>
        <b>Reading Ease Score:</b> {reading_ease}/100<br/>
        <b>Average Sentence Length:</b> {avg_sentence_length} words<br/>
        <b>Average Word Length:</b> {avg_word_length} characters<br/>
        <b>Complex Words:</b> {complex_words_pct}% ({complexity_label})
        """
        
        elements.append(Paragraph(metrics_text, self.styles['QualityMetric']))
        
        # Enhanced interpretation with trustworthiness implications
        interpretation = self._generate_quality_interpretation(grade_level, reading_ease, complex_words_pct)
        elements.append(Paragraph("<b>What This Means:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(interpretation, self.styles['InterpretationText']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _generate_quality_interpretation(self, grade_level: float, reading_ease: float, complex_words: float) -> str:
        """Generate enhanced interpretation of quality metrics with trustworthiness context"""
        interpretation_parts = []
        
        # Grade level interpretation with trustworthiness context
        if grade_level < 6:
            interpretation_parts.append(
                "The transcript uses very simple language (elementary school level), making it highly accessible. "
                "This could indicate clear communication, though very simple language on complex topics might suggest oversimplification."
            )
        elif grade_level < 9:
            interpretation_parts.append(
                "The language is at a middle school level, appropriate for general audiences. "
                "This level is ideal for clear communication without unnecessary complexity."
            )
        elif grade_level < 13:
            interpretation_parts.append(
                "The transcript is at a high school level, suitable for educated audiences. "
                "This suggests thoughtful communication without being needlessly complex."
            )
        else:
            interpretation_parts.append(
                "The language is at a college/graduate level, requiring advanced literacy. "
                "This could indicate sophisticated thinking, or potentially deliberate complexity to obscure meaning."
            )
        
        # Reading ease interpretation
        if reading_ease >= 80:
            interpretation_parts.append("The content is very easy to understand, promoting transparency.")
        elif reading_ease >= 60:
            interpretation_parts.append("The content is reasonably clear and accessible.")
        elif reading_ease >= 30:
            interpretation_parts.append("The content requires focused attention and may not be accessible to all audiences.")
        else:
            interpretation_parts.append("The content is very difficult, which could limit understanding or transparency.")
        
        # Vocabulary complexity with context
        if complex_words < 8:
            interpretation_parts.append("Simple vocabulary suggests direct, honest communication.")
        elif complex_words < 15:
            interpretation_parts.append("Moderate vocabulary shows balance between clarity and precision.")
        else:
            interpretation_parts.append("Complex vocabulary may indicate expertise, or could be used to appear more authoritative than warranted.")
        
        return " ".join(interpretation_parts)
    
    def _create_speaker_quality_section(self, results: Dict) -> List:
        """Create enhanced speaker quality analysis section with trustworthiness focus"""
        elements = []
        
        speaker_quality = results.get('speaker_quality', {})
        
        if not speaker_quality or not speaker_quality.get('success'):
            return elements
        
        elements.append(Paragraph("Speaker Communication Analysis", self.styles['SectionHeader']))
        
        # Get overall assessment
        overall = speaker_quality.get('overall_assessment', {})
        if isinstance(overall, str):
            summary = overall
        elif isinstance(overall, dict):
            grade_level = overall.get('grade_level', 'Unknown')
            summary = overall.get('summary', 'Analysis not available')
            elements.append(Paragraph(f"<b>Communication Level:</b> {grade_level}", self.styles['BodyText']))
        else:
            summary = "Analysis not available"
        
        elements.append(Paragraph(summary, self.styles['BodyText']))
        
        # Get specific metrics
        grade_level_data = speaker_quality.get('grade_level', {})
        language_style = speaker_quality.get('language_style', {})
        sentence_quality = speaker_quality.get('sentence_quality', {})
        coherence = speaker_quality.get('coherence', {})
        vocabulary = speaker_quality.get('vocabulary', {})
        
        metrics_text = []
        
        if grade_level_data:
            grade = grade_level_data.get('flesch_kincaid_grade', 0)
            metrics_text.append(f"<b>Grade Level:</b> {grade:.1f}")
        
        if language_style:
            inflammatory = language_style.get('inflammatory_percentage', 0)
            metrics_text.append(f"<b>Inflammatory Language:</b> {inflammatory:.1f}%")
        
        if sentence_quality:
            completion = sentence_quality.get('completion_rate', 0)
            metrics_text.append(f"<b>Sentence Completion:</b> {completion:.1f}%")
        
        if coherence:
            coherence_score = coherence.get('coherence_score', 0)
            metrics_text.append(f"<b>Coherence:</b> {coherence_score:.1f}/100")
        
        if vocabulary:
            diversity = vocabulary.get('vocabulary_diversity', 0)
            metrics_text.append(f"<b>Vocabulary Diversity:</b> {diversity:.1f}%")
        
        if metrics_text:
            metrics_para = "<br/>".join(metrics_text)
            elements.append(Paragraph(metrics_para, self.styles['QualityMetric']))
        
        # Enhanced interpretation with trustworthiness implications
        elements.append(Paragraph("<b>What This Means:</b>", self.styles['SubsectionHeader']))
        interpretation = self._generate_speaker_interpretation(speaker_quality)
        elements.append(Paragraph(interpretation, self.styles['InterpretationText']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _generate_speaker_interpretation(self, speaker_quality: Dict) -> str:
        """Generate enhanced interpretation of speaker quality with trustworthiness focus"""
        interpretation_parts = []
        
        # Extract metrics
        grade_level_data = speaker_quality.get('grade_level', {})
        language_style = speaker_quality.get('language_style', {})
        sentence_quality = speaker_quality.get('sentence_quality', {})
        coherence = speaker_quality.get('coherence', {})
        
        grade_level_num = grade_level_data.get('flesch_kincaid_grade', 0)
        inflammatory = language_style.get('inflammatory_percentage', 0)
        completion = sentence_quality.get('completion_rate', 100)
        coherence_score = coherence.get('coherence_score', 50)
        
        # Grade level interpretation
        if grade_level_num < 6:
            interpretation_parts.append("The speaker uses very simple language, which promotes accessibility and transparency.")
        elif grade_level_num < 9:
            interpretation_parts.append("The speaker communicates at a level that's clear and accessible to general audiences.")
        elif grade_level_num < 13:
            interpretation_parts.append("The speaker uses moderately sophisticated language appropriate for educated audiences.")
        else:
            interpretation_parts.append("The speaker uses advanced language, which may indicate expertise or could potentially be used to obscure meaning.")
        
        # Inflammatory language - KEY TRUSTWORTHINESS INDICATOR
        if inflammatory < 2:
            interpretation_parts.append("The speaker maintains a neutral, objective tone without emotional manipulation - a strong indicator of trustworthy communication.")
        elif inflammatory < 5:
            interpretation_parts.append("The speaker occasionally uses emotional language but generally remains measured.")
        elif inflammatory < 10:
            interpretation_parts.append("The speaker frequently uses inflammatory language, suggesting reliance on emotional appeals over factual arguments.")
        else:
            interpretation_parts.append("⚠️ WARNING: The speaker heavily relies on inflammatory and manipulative language - a major red flag for credibility.")
        
        # Sentence completion - INDICATOR OF CLEAR THINKING
        if completion > 85:
            interpretation_parts.append("Clear, complete sentences indicate organized thinking and honest communication.")
        elif completion > 70:
            interpretation_parts.append("Mostly complete sentences with occasional fragments.")
        elif completion > 60:
            interpretation_parts.append("Frequent sentence fragments may indicate disorganized thinking or evasive communication.")
        else:
            interpretation_parts.append("⚠️ Very poor sentence completion suggests either unclear thinking or deliberately confusing communication.")
        
        # Coherence - INDICATOR OF LOGICAL THINKING
        if coherence_score >= 75:
            interpretation_parts.append("Strong logical flow suggests well-reasoned, coherent arguments.")
        elif coherence_score >= 60:
            interpretation_parts.append("Adequate logical structure with clear arguments.")
        elif coherence_score >= 40:
            interpretation_parts.append("Weak logical flow may make arguments difficult to follow or verify.")
        else:
            interpretation_parts.append("⚠️ Poor logical coherence raises questions about the validity of arguments.")
        
        return " ".join(interpretation_parts)
    
    def _create_findings_summary_section(self, results: Dict) -> List:
        """Create enhanced summary of findings section with interpretation"""
        elements = []
        
        elements.append(Paragraph("Summary of Findings", self.styles['SectionHeader']))
        
        # Get credibility breakdown
        cred_score = results.get('credibility_score', {})
        breakdown = cred_score.get('breakdown', {})
        score = cred_score.get('score', 0)
        
        # Use the generated summary if available
        if results.get('summary'):
            elements.append(Paragraph(results['summary'], self.styles['BodyText']))
        else:
            # Generate our own summary
            summary_parts = []
            
            true_count = breakdown.get('verified_true', 0)
            false_count = breakdown.get('verified_false', 0)
            partial_count = breakdown.get('partially_accurate', 0)
            unverified_count = breakdown.get('unverifiable', 0)
            
            if true_count > 0:
                summary_parts.append(
                    f"<b>{true_count} claims</b> were verified as true or mostly accurate."
                )
            
            if false_count > 0:
                summary_parts.append(
                    f"<b>{false_count} claims</b> were found to be false or mostly false."
                )
            
            if partial_count > 0:
                summary_parts.append(
                    f"<b>{partial_count} claims</b> were partially accurate or misleading."
                )
            
            if unverified_count > 0:
                summary_parts.append(
                    f"<b>{unverified_count} claims</b> could not be verified with available sources."
                )
            
            findings_summary = " ".join(summary_parts)
            elements.append(Paragraph(findings_summary, self.styles['BodyText']))
        
        # Add enhanced interpretation with actionable insights
        elements.append(Paragraph("<b>What This Means:</b>", self.styles['SubsectionHeader']))
        interpretation = self._generate_findings_interpretation(score, breakdown)
        elements.append(Paragraph(interpretation, self.styles['InterpretationText']))
        
        # Add red flags if significant false claims
        if breakdown.get('verified_false', 0) > 0:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(
                f"⚠️ WARNING: {breakdown['verified_false']} false or misleading claims identified - see detailed analysis below",
                self.styles['RedFlag']
            ))
        
        # Add positive indicator if high accuracy
        if score >= 80:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(
                "✓ High accuracy rate indicates reliable source of information",
                self.styles['PositiveFlag']
            ))
        
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _generate_findings_interpretation(self, score: int, breakdown: Dict) -> str:
        """Generate enhanced interpretation of findings with actionable guidance"""
        true_count = breakdown.get('verified_true', 0)
        false_count = breakdown.get('verified_false', 0)
        total = sum(breakdown.values())
        
        if total == 0:
            return "No claims were analyzed."
        
        true_pct = (true_count / total * 100) if total > 0 else 0
        false_pct = (false_count / total * 100) if total > 0 else 0
        
        interpretation_parts = []
        
        # Overall credibility assessment with clear recommendation
        if score >= 80:
            interpretation_parts.append(
                "✓ <b>HIGH CREDIBILITY:</b> This transcript demonstrates excellent overall credibility. "
                "The vast majority of factual claims are accurate and well-supported. "
                "You can use this content with confidence, though always exercise due diligence on critical decisions."
            )
        elif score >= 60:
            interpretation_parts.append(
                "<b>MOSTLY CREDIBLE:</b> This transcript shows generally reliable content. "
                "While there are some inaccuracies or unverifiable claims, the majority of statements are accurate. "
                "Verify specific facts that are important to your decisions."
            )
        elif score >= 40:
            interpretation_parts.append(
                "⚠️ <b>MIXED CREDIBILITY:</b> This transcript has significant reliability concerns. "
                "There's a substantial balance of accurate and inaccurate claims. "
                "Do not rely on this content without careful verification of all important facts."
            )
        elif score >= 20:
            interpretation_parts.append(
                "⚠️ <b>LOW CREDIBILITY:</b> This transcript has serious credibility problems. "
                "A substantial portion of claims are inaccurate or misleading. "
                "Treat all statements with skepticism and verify independently."
            )
        else:
            interpretation_parts.append(
                "🚫 <b>NOT CREDIBLE:</b> This transcript lacks credibility. "
                "The majority of verifiable claims are false or misleading. "
                "Do not rely on this content. The source has demonstrated unreliability."
            )
        
        # Specific guidance based on false claims
        if false_count > 0:
            interpretation_parts.append(
                f" The {false_count} false claims identified represent significant factual errors that "
                "undermine the overall credibility of this source."
            )
        
        # Specific guidance based on accuracy rate
        if true_pct > 70:
            interpretation_parts.append(
                " The high percentage of accurate claims suggests the speaker generally relies on factual information."
            )
        
        # Guidance on unverifiable claims
        unverified = breakdown.get('unverifiable', 0)
        if unverified > total * 0.5:
            interpretation_parts.append(
                f" However, {unverified} claims could not be verified, which may indicate vague statements, "
                "future predictions, or topics requiring specialized fact-checking resources."
            )
        
        return " ".join(interpretation_parts)
    
    def _create_claims_evaluation_section(self, results: Dict) -> List:
        """
        Create detailed evaluation of every single claim
        THIS IS THE KEY SECTION - Each claim gets full treatment
        """
        elements = []
        
        elements.append(Paragraph("Detailed Claim Evaluations", self.styles['SectionHeader']))
        elements.append(Paragraph(
            "Each claim from the transcript is quoted below with its complete evaluation and sources.",
            self.styles['BodyText']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Get all fact-checked claims (backward compatible)
        fact_checks = results.get('fact_checks') or results.get('claims', [])
        
        if not fact_checks:
            elements.append(Paragraph(
                "No claims were found that could be fact-checked.",
                self.styles['BodyText']
            ))
            return elements
        
        logger.info(f"[PDF Generator] Processing {len(fact_checks)} claims for PDF")
        
        # Process each claim
        for i, claim_data in enumerate(fact_checks, 1):
            # Keep each claim together on one page if possible
            claim_elements = self._create_single_claim_section(i, claim_data)
            elements.append(KeepTogether(claim_elements))
            
            # Add spacing between claims
            if i < len(fact_checks):
                elements.append(Spacer(1, 0.3*inch))
        
        logger.info(f"[PDF Generator] ✓ Added all {len(fact_checks)} claims to PDF")
        
        return elements
    
    def _create_single_claim_section(self, claim_number: int, claim_data: Dict) -> List:
        """
        Create a detailed section for a single claim
        Each claim gets: Number, Quote, Speaker, Verdict, Evaluation, Sources
        """
        elements = []
        
        # Claim number
        elements.append(Paragraph(
            f"Claim #{claim_number}",
            self.styles['ClaimNumber']
        ))
        
        # Speaker info (if available)
        speaker = claim_data.get('speaker', 'Unknown')
        if speaker and speaker != 'Unknown':
            elements.append(Paragraph(
                f"Speaker: {speaker}",
                self.styles['SpeakerInfo']
            ))
        
        # The actual claim (quoted and highlighted)
        # Handle both 'claim' and 'text' keys (backward compatible)
        claim_text = claim_data.get('claim') or claim_data.get('text', 'No claim text available')
        elements.append(Paragraph(
            f'"{claim_text}"',
            self.styles['ClaimText']
        ))
        
        # Verdict (with appropriate color)
        verdict = claim_data.get('verdict', 'unverifiable').lower()
        verdict_text = self._format_verdict_text(verdict)
        verdict_style = self._get_verdict_style(verdict)
        
        elements.append(Paragraph(
            f"<b>Verdict:</b> {verdict_text}",
            verdict_style
        ))
        
        # Confidence (if available)
        confidence = claim_data.get('confidence')
        if confidence and confidence > 0:
            elements.append(Paragraph(
                f"<b>Confidence:</b> {confidence}%",
                self.styles['BodyText']
            ))
        
        # Evaluation/Explanation (the detailed analysis)
        explanation = claim_data.get('explanation', 'No explanation available.')
        elements.append(Paragraph(
            "<b>Evaluation:</b>",
            self.styles['SubsectionHeader']
        ))
        elements.append(Paragraph(
            explanation,
            self.styles['EvaluationText']
        ))
        
        # Sources (if available)
        sources = claim_data.get('sources', [])
        if sources and len(sources) > 0:
            elements.append(Paragraph(
                "<b>Sources:</b>",
                self.styles['SubsectionHeader']
            ))
            for source in sources:
                if source:  # Make sure source isn't empty
                    elements.append(Paragraph(
                        f"• {source}",
                        self.styles['SourceCitation']
                    ))
        
        return elements
    
    def _format_verdict_text(self, verdict: str) -> str:
        """Format verdict for display"""
        verdict_map = {
            'true': 'TRUE',
            'verified_true': 'TRUE',
            'mostly_true': 'MOSTLY TRUE',
            'false': 'FALSE',
            'verified_false': 'FALSE',
            'mostly_false': 'MOSTLY FALSE',
            'misleading': 'MISLEADING',
            'partially_accurate': 'PARTIALLY ACCURATE',
            'partially_true': 'PARTIALLY TRUE',
            'mixed': 'MIXED',
            'unverifiable': 'UNVERIFIABLE',
            'needs_context': 'NEEDS CONTEXT',
            'opinion': 'OPINION/SUBJECTIVE'
        }
        return verdict_map.get(verdict.lower(), verdict.upper())
    
    def _get_verdict_style(self, verdict: str) -> ParagraphStyle:
        """Get the appropriate style for a verdict"""
        verdict_lower = verdict.lower()
        
        if verdict_lower in ['true', 'verified_true', 'mostly_true']:
            return self.styles['VerdictTrue']
        elif verdict_lower in ['false', 'verified_false', 'mostly_false', 'misleading']:
            return self.styles['VerdictFalse']
        elif verdict_lower in ['mixed', 'partially_accurate', 'partially_true', 'needs_context']:
            return self.styles['VerdictMixed']
        else:
            return self.styles['VerdictUnverifiable']


logger.info("[PDF Generator v3.0.0] ✓ Comprehensive PDF generator with trustworthiness assessment loaded!")

# I did no harm and this file is not truncated
