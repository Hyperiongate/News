"""
File: services/transcript_pdf_generator.py
Created: October 24, 2025
Last Updated: November 5, 2025 - v2.0.0 COMPREHENSIVE PDF WITH ALL SECTIONS
Version: 2.0.0
Description: Professional PDF reports for transcript fact-checking with complete analysis

LATEST UPDATE (November 5, 2025 - v2.0.0 COMPREHENSIVE PDF):
=============================================================
✅ ADDED: Complete claim documentation (all claims verbatim with evaluations)
✅ ADDED: Transcript quality analysis section (grade level, readability, complexity)
✅ ADDED: Speaker quality analysis section (if available)
✅ ADDED: Comprehensive "What This Means" interpretation for every section
✅ ADDED: Professional formatting with detailed subsections
✅ FIXED: Backward compatibility - works with both 'claims' and 'fact_checks' keys
✅ FIXED: Handles missing fields gracefully (DO NO HARM)
✅ ENHANCED: Summary of Findings with interpretation
✅ ENHANCED: Content Summary with context
✅ ENHANCED: Every claim shown verbatim with full evaluation

WHAT'S IN THE PDF NOW:
======================
1. Title Page with date and job ID
2. Trust Score (BIG and prominent with color)
3. Summary of Content (transcript overview, claims count, speakers, topics)
4. Transcript Quality Analysis (NEW - grade level, readability, complexity)
5. Speaker Quality Analysis (NEW - if available)
6. Summary of Findings (what was found + what it means)
7. Detailed Claim Evaluations (EVERY claim verbatim with full analysis)
   - Claim number
   - Speaker (if known)
   - Full quote (highlighted)
   - Verdict (color-coded)
   - Confidence score
   - Detailed evaluation
   - Sources cited

BACKWARD COMPATIBILITY:
=======================
✅ Works with 'claims' key (old format)
✅ Works with 'fact_checks' key (new format)
✅ Gracefully handles missing fields
✅ Never crashes on missing data

This is a COMPLETE file ready for deployment.
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
    Generate professional PDF reports for transcript analysis
    
    v2.0.0: Complete sections with comprehensive analysis and interpretation
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create custom styles optimized for transcript reports"""
        
        # Main title
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Title'],
            fontSize=26,
            textColor=HexColor('#1f2937'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle
        self.styles.add(ParagraphStyle(
            name='ReportSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor('#6b7280'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Trust Score (BIG and prominent)
        self.styles.add(ParagraphStyle(
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
        self.styles.add(ParagraphStyle(
            name='TrustLabel',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=HexColor('#4b5563'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section headers
        self.styles.add(ParagraphStyle(
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
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#374151'),
            spaceAfter=8,
            spaceBefore=16,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
        
        # Claim number
        self.styles.add(ParagraphStyle(
            name='ClaimNumber',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=HexColor('#3b82f6'),
            fontName='Helvetica-Bold',
            spaceAfter=8,
            spaceBefore=20
        ))
        
        # Claim text (the actual quote)
        self.styles.add(ParagraphStyle(
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
        self.styles.add(ParagraphStyle(
            name='VerdictTrue',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=HexColor('#059669'),
            fontName='Helvetica-Bold',
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='VerdictFalse',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=HexColor('#dc2626'),
            fontName='Helvetica-Bold',
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='VerdictMixed',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=HexColor('#d97706'),
            fontName='Helvetica-Bold',
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='VerdictUnverifiable',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=HexColor('#6b7280'),
            fontName='Helvetica-Bold',
            spaceAfter=8
        ))
        
        # Evaluation text
        self.styles.add(ParagraphStyle(
            name='EvaluationText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leftIndent=10
        ))
        
        # Speaker info
        self.styles.add(ParagraphStyle(
            name='SpeakerInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#6b7280'),
            fontName='Helvetica-Oblique',
            spaceAfter=4
        ))
        
        # Source citation
        self.styles.add(ParagraphStyle(
            name='SourceCitation',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=HexColor('#6b7280'),
            leftIndent=10,
            spaceAfter=4
        ))
        
        # Quality metric
        self.styles.add(ParagraphStyle(
            name='QualityMetric',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            spaceAfter=8
        ))
        
        # Interpretation text
        self.styles.add(ParagraphStyle(
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
            logger.info(f"[PDF Generator] Starting PDF generation to {output_path}")
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
            
            # 3. SUMMARY OF CONTENT
            story.extend(self._create_content_summary_section(results))
            
            # 4. TRANSCRIPT QUALITY ANALYSIS (NEW v2.0)
            if results.get('transcript_quality'):
                story.extend(self._create_transcript_quality_section(results))
            
            # 5. SPEAKER QUALITY ANALYSIS (NEW v2.0)
            if results.get('speaker_quality'):
                story.extend(self._create_speaker_quality_section(results))
            
            # 6. SUMMARY OF FINDINGS
            story.extend(self._create_findings_summary_section(results))
            
            # Page break before claims
            story.append(PageBreak())
            
            # 7. DETAILED CLAIM EVALUATIONS (THE KEY SECTION)
            story.extend(self._create_claims_evaluation_section(results))
            
            # Build PDF
            doc.build(story)
            logger.info(f"[PDF Generator] ✓ PDF generated successfully: {output_path}")
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
        """Create transcript quality analysis section (NEW v2.0)"""
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
        
        # Interpretation
        interpretation = self._generate_quality_interpretation(grade_level, reading_ease, complex_words_pct)
        elements.append(Paragraph("<b>What This Means:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(interpretation, self.styles['InterpretationText']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _generate_quality_interpretation(self, grade_level: float, reading_ease: float, complex_words: float) -> str:
        """Generate interpretation of quality metrics"""
        interpretation_parts = []
        
        # Grade level interpretation
        if grade_level < 6:
            interpretation_parts.append("The transcript is written at an elementary school level, making it very accessible to a broad audience.")
        elif grade_level < 9:
            interpretation_parts.append("The transcript is written at a middle school level, appropriate for general audiences.")
        elif grade_level < 13:
            interpretation_parts.append("The transcript is written at a high school level, suitable for educated audiences.")
        else:
            interpretation_parts.append("The transcript is written at a college level, requiring advanced literacy skills.")
        
        # Reading ease interpretation
        if reading_ease >= 80:
            interpretation_parts.append("The language is very easy to read and understand.")
        elif reading_ease >= 60:
            interpretation_parts.append("The language is reasonably easy to read for most people.")
        elif reading_ease >= 30:
            interpretation_parts.append("The language is fairly difficult and may require focused attention.")
        else:
            interpretation_parts.append("The language is very difficult and may be challenging for many readers.")
        
        # Vocabulary complexity
        if complex_words < 8:
            interpretation_parts.append("The speaker uses simple, everyday vocabulary.")
        elif complex_words < 15:
            interpretation_parts.append("The speaker uses moderate vocabulary with some complex terms.")
        else:
            interpretation_parts.append("The speaker frequently uses advanced, multi-syllable words.")
        
        return " ".join(interpretation_parts)
    
    def _create_speaker_quality_section(self, results: Dict) -> List:
        """Create speaker quality analysis section (NEW v2.0)"""
        elements = []
        
        speaker_quality = results.get('speaker_quality', {})
        
        if not speaker_quality or not speaker_quality.get('success'):
            return elements
        
        elements.append(Paragraph("Speaker Quality Analysis", self.styles['SectionHeader']))
        
        # Get overall assessment
        overall = speaker_quality.get('overall_assessment', {})
        grade_level = overall.get('grade_level', 'Unknown')
        summary = overall.get('summary', 'Analysis not available')
        
        elements.append(Paragraph(f"<b>Communication Level:</b> {grade_level}", self.styles['BodyText']))
        elements.append(Paragraph(summary, self.styles['BodyText']))
        
        # Get specific metrics
        metrics = speaker_quality.get('metrics', {})
        
        if metrics:
            metrics_text = []
            
            if 'grade_level' in metrics:
                metrics_text.append(f"<b>Grade Level:</b> {metrics['grade_level']}")
            
            if 'inflammatory_language_pct' in metrics:
                inflammatory = metrics['inflammatory_language_pct']
                metrics_text.append(f"<b>Inflammatory Language:</b> {inflammatory}%")
            
            if 'sentence_completion_pct' in metrics:
                completion = metrics['sentence_completion_pct']
                metrics_text.append(f"<b>Sentence Completion:</b> {completion}%")
            
            if 'vocabulary_diversity_pct' in metrics:
                diversity = metrics['vocabulary_diversity_pct']
                metrics_text.append(f"<b>Vocabulary Diversity:</b> {diversity}%")
            
            if metrics_text:
                metrics_para = "<br/>".join(metrics_text)
                elements.append(Paragraph(metrics_para, self.styles['QualityMetric']))
        
        # Interpretation
        elements.append(Paragraph("<b>What This Means:</b>", self.styles['SubsectionHeader']))
        interpretation = self._generate_speaker_interpretation(overall, metrics)
        elements.append(Paragraph(interpretation, self.styles['InterpretationText']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _generate_speaker_interpretation(self, overall: Dict, metrics: Dict) -> str:
        """Generate interpretation of speaker quality"""
        interpretation_parts = []
        
        # Grade level interpretation
        grade_level_num = metrics.get('grade_level', 0)
        if grade_level_num < 6:
            interpretation_parts.append("The speaker communicates in very simple, accessible language.")
        elif grade_level_num < 9:
            interpretation_parts.append("The speaker uses clear, straightforward language appropriate for general audiences.")
        elif grade_level_num < 13:
            interpretation_parts.append("The speaker uses moderately complex language suitable for educated audiences.")
        else:
            interpretation_parts.append("The speaker uses sophisticated, academic language.")
        
        # Inflammatory language
        inflammatory = metrics.get('inflammatory_language_pct', 0)
        if inflammatory < 2:
            interpretation_parts.append("The tone remains neutral and objective.")
        elif inflammatory < 5:
            interpretation_parts.append("There are occasional emotional appeals but the tone is largely measured.")
        else:
            interpretation_parts.append("The language contains notable emotional or inflammatory rhetoric.")
        
        # Sentence completion
        completion = metrics.get('sentence_completion_pct', 100)
        if completion > 85:
            interpretation_parts.append("The speaker completes thoughts clearly and coherently.")
        elif completion > 60:
            interpretation_parts.append("The speaker occasionally uses incomplete sentences or fragments.")
        else:
            interpretation_parts.append("The speech frequently contains incomplete thoughts and fragmented sentences.")
        
        return " ".join(interpretation_parts)
    
    def _create_findings_summary_section(self, results: Dict) -> List:
        """Create summary of findings section with interpretation"""
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
        
        # Add interpretation
        elements.append(Paragraph("<b>What This Means:</b>", self.styles['SubsectionHeader']))
        interpretation = self._generate_findings_interpretation(score, breakdown)
        elements.append(Paragraph(interpretation, self.styles['InterpretationText']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _generate_findings_interpretation(self, score: int, breakdown: Dict) -> str:
        """Generate interpretation of findings"""
        true_count = breakdown.get('verified_true', 0)
        false_count = breakdown.get('verified_false', 0)
        total = sum(breakdown.values())
        
        if total == 0:
            return "No claims were analyzed."
        
        true_pct = (true_count / total * 100) if total > 0 else 0
        false_pct = (false_count / total * 100) if total > 0 else 0
        
        interpretation_parts = []
        
        # Overall credibility assessment
        if score >= 80:
            interpretation_parts.append("This transcript demonstrates high overall credibility. The vast majority of factual claims are accurate and well-supported.")
        elif score >= 60:
            interpretation_parts.append("This transcript shows mostly credible content. While there are some inaccuracies or unverifiable claims, the majority of statements are accurate.")
        elif score >= 40:
            interpretation_parts.append("This transcript has mixed credibility. There's a significant balance of accurate and inaccurate claims, requiring careful verification of specific statements.")
        elif score >= 20:
            interpretation_parts.append("This transcript has low credibility. A substantial portion of claims are inaccurate or misleading.")
        else:
            interpretation_parts.append("This transcript lacks credibility. The majority of verifiable claims are false or misleading.")
        
        # Specific guidance
        if false_count > 0:
            interpretation_parts.append(f"Pay particular attention to the {false_count} claims identified as false or misleading, as these represent significant factual errors.")
        
        if true_pct > 70:
            interpretation_parts.append("The high percentage of accurate claims suggests the speaker generally relies on factual information.")
        
        unverified = breakdown.get('unverifiable', 0)
        if unverified > total * 0.5:
            interpretation_parts.append("A large number of claims could not be verified, which may indicate vague statements, future predictions, or topics requiring specialized fact-checking resources.")
        
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


logger.info("[PDF Generator v2.0.0] ✓ Comprehensive PDF generator with all sections loaded!")

# I did no harm and this file is not truncated
