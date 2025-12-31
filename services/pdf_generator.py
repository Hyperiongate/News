# services/pdf_generator.py
"""
PDF Generation Service - v4.0 - GRAMMAR REMOVED
Creates professional PDF reports from analysis results

CRITICAL CHANGE IN v4.0 (December 30, 2025):
❌ GRAMMAR ANALYSIS COMPLETELY REMOVED FROM PDFS
- User feedback: False grammar errors destroy trust
- Backend v6.0 no longer provides grammar data
- PDFs no longer include grammar sections
- Philosophy: Better NO grammar than WRONG grammar

WHAT WAS REMOVED IN v4.0:
- ❌ Grammar sections from Content Quality PDFs
- ❌ Grammar metrics from summaries
- ❌ Grammar-related fallback text
- ❌ Any mention of grammar errors in analysis

WHAT STAYS (unchanged):
- ✅ All other content quality metrics (readability, vocabulary, structure)
- ✅ All 6 other service sections
- ✅ Extraction logic from v3.2
- ✅ Bias bar graphics
- ✅ Professional formatting

PRESERVED FROM v3.2:
✅ extract_text() method that matches JavaScript logic
✅ Recursive deep search through data structures
✅ All section creation methods
✅ Page numbering and styling

I did no harm (removed harmful false positives) and this file is not truncated.
Date: December 30, 2025
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
    """Generate PDF reports from analysis results - v4.0 WITHOUT GRAMMAR"""
    
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
        
        # Get detailed_analysis for all services
        detailed = analysis_data.get('detailed_analysis', {})
        
        # Add ALL 7 service sections (Content Quality WITHOUT GRAMMAR)
        
        # 1. Source Credibility
        if 'source_credibility' in detailed:
            story.extend(self._create_source_credibility_section(detailed['source_credibility']))
            story.append(PageBreak())
        
        # 2. Bias Detection
        if 'bias_detector' in detailed:
            story.extend(self._create_bias_detector_section(detailed['bias_detector']))
            story.append(PageBreak())
        elif analysis_data.get('bias_analysis'):  # Fallback to old structure
            story.extend(self._create_bias_section(analysis_data.get('bias_analysis', {})))
            story.append(PageBreak())
        
        # 3. Fact Checking
        if 'fact_checker' in detailed or analysis_data.get('fact_checks'):
            fact_data = detailed.get('fact_checker', {})
            fact_checks = analysis_data.get('fact_checks', [])
            story.extend(self._create_fact_check_section(fact_data, fact_checks))
            story.append(PageBreak())
        
        # 4. Author Analysis
        if 'author_analyzer' in detailed or analysis_data.get('author_info'):
            author_data = detailed.get('author_analyzer', analysis_data.get('author_info', {}))
            story.extend(self._create_author_section(author_data))
            story.append(PageBreak())
        
        # 5. Transparency
        if 'transparency_analyzer' in detailed:
            story.extend(self._create_transparency_section(detailed['transparency_analyzer']))
            story.append(PageBreak())
        
        # 6. Manipulation Detection
        if 'manipulation_detector' in detailed:
            story.extend(self._create_manipulation_section(detailed['manipulation_detector']))
            story.append(PageBreak())
        
        # 7. Content Quality (v4.0: NO GRAMMAR SECTIONS)
        if 'content_analyzer' in detailed:
            story.extend(self._create_content_quality_section(detailed['content_analyzer']))
            story.append(PageBreak())
        
        # Add additional sections (legacy)
        story.extend(self._create_additional_sections(analysis_data))
        
        # Add footer
        story.extend(self._create_footer())
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        buffer.seek(0)
        
        return buffer
    
    # ========================================================================
    # EXTRACTION LOGIC (v3.2 - preserved)
    # ========================================================================
    
    def extract_text(self, value, fallback='No information available.'):
        """
        EXACT PYTHON REPLICATION of service-templates.js extractText() function
        
        Recursively searches through:
        - Direct strings
        - Arrays (checks first element)
        - Objects (checks 20+ field names, finds long strings, recurses deeply)
        - Numbers/booleans (converts to string)
        
        Returns the first meaningful text found, or fallback if nothing found.
        """
        
        # Direct string
        if isinstance(value, str):
            text = value.strip()
            if len(text) > 20:
                return text
        
        # Array - check first element
        elif isinstance(value, list):
            if value:
                return self.extract_text(value[0], fallback)
        
        # Number or boolean
        elif isinstance(value, (int, float, bool)):
            return str(value)
        
        # Object (dict) - THE CRITICAL RECURSIVE SEARCH
        elif isinstance(value, dict):
            # List of field names to check (matches JavaScript exactly)
            field_names = [
                'text', 'content', 'analysis', 'summary', 'description',
                'explanation', 'details', 'message', 'result', 'findings',
                'interpretation', 'conclusion', 'assessment', 'verdict',
                'what_we_found', 'what_we_looked', 'what_it_means',
                'what_we_analyzed', 'insight', 'data', 'value'
            ]
            
            # Check each field name
            for field in field_names:
                if field in value:
                    found_text = self.extract_text(value[field], None)
                    if found_text and found_text != fallback:
                        return found_text
            
            # Look for any long string value (>20 chars)
            for key, val in value.items():
                if isinstance(val, str):
                    text = val.strip()
                    if len(text) > 20:
                        return text
            
            # Recursively check all nested objects
            for key, val in value.items():
                if isinstance(val, dict):
                    found_text = self.extract_text(val, None)
                    if found_text and found_text != fallback:
                        return found_text
        
        # Nothing found - return fallback
        return fallback
    
    def _extract_analysis_text(self, service_data, service_name):
        """
        Extract the 3-part analysis text (what_we_looked, what_we_found, what_it_means)
        v4.0: Updated to exclude grammar references
        """
        
        analysis = service_data.get('data', {}).get('analysis', {})
        
        if not isinstance(analysis, dict):
            analysis = service_data.get('analysis', {})
        
        # WHAT WE LOOKED AT - will recursively search EVERYWHERE!
        what_we_looked = self.extract_text(
            analysis.get('what_we_looked') or analysis.get('what_we_analyzed') or analysis,
            self._generate_what_we_looked_fallback(service_name, service_data)
        )
        
        # WHAT WE FOUND - will recursively search EVERYWHERE!
        what_we_found = self.extract_text(
            analysis.get('what_we_found') or analysis.get('findings') or analysis,
            self._generate_what_we_found_fallback(service_name, service_data)
        )
        
        # WHAT IT MEANS - will recursively search EVERYWHERE!
        what_it_means = self.extract_text(
            analysis.get('what_it_means') or analysis.get('interpretation') or analysis.get('conclusion') or analysis,
            self._generate_what_it_means_fallback(service_name, service_data)
        )
        
        result = {
            'what_we_looked': what_we_looked,
            'what_we_found': what_we_found,
            'what_it_means': what_it_means
        }
        
        logger.info(f"[PDFGen v4.0] Successfully extracted analysis text for {service_name}")
        return result
    
    # ========================================================================
    # FALLBACK GENERATORS (v4.0: NO GRAMMAR MENTIONS)
    # ========================================================================
    
    def _generate_what_we_looked_fallback(self, service_name, data):
        """
        Generate fallback for what_we_looked
        v4.0: Updated Content Quality to exclude grammar
        """
        templates = {
            'Source Credibility': 'We analyzed source reputation, domain authority, editorial standards, and historical accuracy.',
            'Bias Detection': 'We examined language patterns, framing choices, source selection, and political indicators.',
            'Fact Checking': 'We extracted factual claims and verified them against authoritative sources.',
            'Author Analysis': 'We investigated author credentials, publication history, expertise, and verification status.',
            'Transparency': 'We evaluated source attribution, citation quality, and disclosure practices.',
            'Manipulation Detection': 'We analyzed content for emotional manipulation tactics and persuasive techniques.',
            'Content Quality': 'We assessed writing quality, readability, structure, vocabulary, and professional sourcing. We do not currently evaluate grammar mechanics.'
        }
        return templates.get(service_name, f'We performed comprehensive {service_name.lower()} analysis.')
    
    def _generate_what_we_found_fallback(self, service_name, data):
        """
        Generate fallback for what_we_found
        v4.0: No grammar error mentions
        """
        score = data.get('score', data.get('credibility_score', data.get('quality_score', 50)))
        return f'Analysis completed with a score of {score}/100.'
    
    def _generate_what_it_means_fallback(self, service_name, data):
        """
        Generate fallback for what_it_means
        v4.0: No grammar references
        """
        score = data.get('score', data.get('credibility_score', data.get('quality_score', 50)))
        
        if score >= 80:
            return f'This {service_name.lower()} score indicates excellent credibility and professional standards.'
        elif score >= 60:
            return f'This {service_name.lower()} score indicates good credibility with minor areas for improvement.'
        else:
            return f'This {service_name.lower()} score indicates concerns that warrant careful verification.'
    
    def _generate_generic_analysis(self, service_name):
        """
        Generate generic analysis text as last resort fallback
        v4.0: No grammar mentions
        """
        return {
            'what_we_looked': f"We performed comprehensive {service_name.lower()} analysis on this content.",
            'what_we_found': f"Analysis completed and results have been processed.",
            'what_it_means': f"This analysis provides insight into the content's {service_name.lower()} characteristics."
        }
    
    # ========================================================================
    # CONTENT QUALITY SECTION (v4.0: NO GRAMMAR)
    # ========================================================================
    
    def _create_content_quality_section(self, service_data):
        """
        Create content quality section WITHOUT GRAMMAR
        v4.0: Grammar sections completely removed
        """
        elements = []
        
        elements.append(Paragraph("Content Quality", self.styles['SectionHeader']))
        
        # Score
        score = service_data.get('score', service_data.get('quality_score', 50))
        elements.append(Paragraph(f"<b>Score:</b> {score}/100", self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Extract analysis text (NO GRAMMAR)
        analysis = self._extract_analysis_text(service_data, "Content Quality")
        
        elements.append(Paragraph("<b>What We Analyzed:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_we_looked'], self.styles['CustomBody']))
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph("<b>What We Found:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_we_found'], self.styles['CustomBody']))
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph("<b>What It Means:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_it_means'], self.styles['CustomBody']))
        
        # ❌ REMOVED: Grammar sections that were in v3.2
        
        # Add quality metrics (NO GRAMMAR)
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("<b>Quality Metrics:</b>", self.styles['SubsectionHeader']))
        
        metrics_data = service_data.get('data', {}).get('metrics', {})
        
        # Show metrics WITHOUT grammar
        metrics_list = []
        
        if 'readability' in metrics_data:
            read_score = metrics_data['readability'].get('score', 0)
            grade = metrics_data['readability'].get('grade_level', 'Unknown')
            metrics_list.append(f"Readability: {read_score}/100 ({grade})")
        
        if 'structure' in metrics_data:
            struct_score = metrics_data['structure'].get('score', 0)
            para_count = metrics_data['structure'].get('paragraph_count', 0)
            metrics_list.append(f"Structure: {struct_score}/100 ({para_count} paragraphs)")
        
        if 'vocabulary' in metrics_data:
            vocab_score = metrics_data['vocabulary'].get('score', 0)
            diversity = int(metrics_data['vocabulary'].get('diversity_ratio', 0) * 100)
            metrics_list.append(f"Vocabulary: {vocab_score}/100 ({diversity}% unique words)")
        
        # ❌ REMOVED: Grammar metric that was in v3.2
        
        if 'professionalism' in metrics_data:
            prof_score = metrics_data['professionalism'].get('score', 0)
            citations = metrics_data['professionalism'].get('citation_count', 0)
            metrics_list.append(f"Professionalism: {prof_score}/100 ({citations} citations)")
        
        if 'coherence' in metrics_data:
            coh_score = metrics_data['coherence'].get('score', 0)
            connectors = metrics_data['coherence'].get('connector_count', 0)
            metrics_list.append(f"Coherence: {coh_score}/100 ({connectors} transitions)")
        
        # Add metrics to PDF
        for metric in metrics_list:
            elements.append(Paragraph(f"• {metric}", self.styles['CustomBody']))
        
        return elements
    
    # ========================================================================
    # ALL OTHER SECTION METHODS (unchanged from v3.2)
    # ========================================================================
    
    def _create_source_credibility_section(self, service_data):
        """Create source credibility section with extract_text() logic"""
        elements = []
        
        elements.append(Paragraph("Source Credibility Analysis", self.styles['SectionHeader']))
        
        # Score
        score = service_data.get('score', service_data.get('credibility_score', 50))
        elements.append(Paragraph(f"<b>Score:</b> {score}/100", self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Extract analysis text using extract_text() method
        analysis = self._extract_analysis_text(service_data, "Source Credibility")
        
        elements.append(Paragraph("<b>What We Analyzed:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_we_looked'], self.styles['CustomBody']))
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph("<b>What We Found:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_we_found'], self.styles['CustomBody']))
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph("<b>What It Means:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_it_means'], self.styles['CustomBody']))
        
        return elements
    
    def _create_bias_detector_section(self, service_data):
        """Create bias detector section with extract_text() logic"""
        elements = []
        
        elements.append(Paragraph("Bias Analysis", self.styles['SectionHeader']))
        
        # Score
        score = service_data.get('score', service_data.get('objectivity_score', 50))
        elements.append(Paragraph(f"<b>Objectivity Score:</b> {score}/100", self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Extract analysis text using extract_text() method
        analysis = self._extract_analysis_text(service_data, "Bias Detection")
        
        elements.append(Paragraph("<b>What We Analyzed:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_we_looked'], self.styles['CustomBody']))
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph("<b>What We Found:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_we_found'], self.styles['CustomBody']))
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph("<b>What It Means:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_it_means'], self.styles['CustomBody']))
        
        return elements
    
    def _create_fact_check_section(self, fact_data, fact_checks):
        """Create fact checking section with extract_text() logic"""
        elements = []
        
        elements.append(Paragraph("Fact Checking", self.styles['SectionHeader']))
        
        # Score
        score = fact_data.get('score', fact_data.get('accuracy_score', 50))
        elements.append(Paragraph(f"<b>Accuracy Score:</b> {score}/100", self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Extract analysis text using extract_text() method
        analysis = self._extract_analysis_text(fact_data, "Fact Checking")
        
        elements.append(Paragraph("<b>What We Analyzed:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_we_looked'], self.styles['CustomBody']))
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph("<b>What We Found:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_we_found'], self.styles['CustomBody']))
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph("<b>What It Means:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_it_means'], self.styles['CustomBody']))
        
        # Statistics
        if fact_checks:
            total = len(fact_checks)
            verified = sum(1 for fc in fact_checks if fc.get('verdict', '').lower() in ['true', 'verified'])
            
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(f"<b>Total Claims Checked:</b> {total}", self.styles['CustomBody']))
            elements.append(Paragraph(f"<b>Verified as True:</b> {verified} ({int(verified/total*100) if total > 0 else 0}%)", 
                                    self.styles['CustomBody']))
        
        return elements
    
    def _create_author_section(self, author_data):
        """Create author analysis section with extract_text() logic"""
        elements = []
        
        elements.append(Paragraph("Author Analysis", self.styles['SectionHeader']))
        
        # Score
        score = author_data.get('score', author_data.get('credibility_score', 50))
        elements.append(Paragraph(f"<b>Score:</b> {score}/100", self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Extract analysis text using extract_text() method
        analysis = self._extract_analysis_text(author_data, "Author Analysis")
        
        elements.append(Paragraph("<b>What We Analyzed:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_we_looked'], self.styles['CustomBody']))
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph("<b>What We Found:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_we_found'], self.styles['CustomBody']))
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph("<b>What It Means:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_it_means'], self.styles['CustomBody']))
        
        # Author details
        author_name = author_data.get('name', author_data.get('author_name', 'Unknown'))
        if author_name and author_name != 'Unknown':
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(f"<b>Author:</b> {author_name}", self.styles['CustomBody']))
        
        return elements
    
    def _create_transparency_section(self, service_data):
        """Create transparency section with extract_text() logic"""
        elements = []
        
        elements.append(Paragraph("Transparency Assessment", self.styles['SectionHeader']))
        
        # Score
        score = service_data.get('score', service_data.get('transparency_score', 50))
        elements.append(Paragraph(f"<b>Score:</b> {score}/100", self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Extract analysis text using extract_text() method
        analysis = self._extract_analysis_text(service_data, "Transparency")
        
        elements.append(Paragraph("<b>What We Analyzed:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_we_looked'], self.styles['CustomBody']))
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph("<b>What We Found:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_we_found'], self.styles['CustomBody']))
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph("<b>What It Means:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_it_means'], self.styles['CustomBody']))
        
        return elements
    
    def _create_manipulation_section(self, service_data):
        """Create manipulation detection section with extract_text() logic"""
        elements = []
        
        elements.append(Paragraph("Manipulation Detection", self.styles['SectionHeader']))
        
        # Score
        score = service_data.get('score', service_data.get('integrity_score', 50))
        elements.append(Paragraph(f"<b>Score:</b> {score}/100", self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Extract analysis text using extract_text() method
        analysis = self._extract_analysis_text(service_data, "Manipulation Detection")
        
        elements.append(Paragraph("<b>What We Analyzed:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_we_looked'], self.styles['CustomBody']))
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph("<b>What We Found:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_we_found'], self.styles['CustomBody']))
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph("<b>What It Means:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(analysis['what_it_means'], self.styles['CustomBody']))
        
        return elements
    
    # ========================================================================
    # LEGACY SECTIONS
    # ========================================================================
    
    def _create_bias_section(self, bias_data):
        """Legacy bias section (fallback)"""
        elements = []
        
        elements.append(Paragraph("Political Bias Analysis", self.styles['SectionHeader']))
        
        # Bias score and direction
        bias_score = bias_data.get('bias_score', 0)
        bias_direction = bias_data.get('bias_direction', 'neutral')
        
        elements.append(Paragraph(f"<b>Bias Direction:</b> {bias_direction.title()}", 
                                self.styles['CustomBody']))
        elements.append(Paragraph(f"<b>Bias Intensity:</b> {abs(bias_score)}/100", 
                                self.styles['CustomBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Create bias visualization
        drawing = Drawing(400, 50)
        
        # Background bar
        drawing.add(Rect(0, 15, 400, 20, fillColor=colors.HexColor('#e5e7eb'), 
                        strokeColor=None))
        
        # Center line
        drawing.add(Line(200, 10, 200, 40, strokeColor=colors.HexColor('#6b7280'), 
                        strokeWidth=2))
        
        # Bias indicator
        if bias_direction == 'left':
            indicator_x = 200 - (abs(bias_score) * 2)
            color = colors.HexColor('#3b82f6')
        elif bias_direction == 'right':
            indicator_x = 200 + (abs(bias_score) * 2)
            color = colors.HexColor('#ef4444')
        else:
            indicator_x = 200
            color = colors.HexColor('#10b981')
        
        drawing.add(Circle(indicator_x, 25, 8, fillColor=color, strokeColor=None))
        
        # Labels
        drawing.add(String(10, 0, "Left", fontSize=10, fillColor=colors.HexColor('#3b82f6')))
        drawing.add(String(180, 0, "Center", fontSize=10, fillColor=colors.HexColor('#6b7280')))
        drawing.add(String(360, 0, "Right", fontSize=10, fillColor=colors.HexColor('#ef4444')))
        
        elements.append(drawing)
        elements.append(Spacer(1, 0.3*inch))
        
        # Analysis text
        if bias_data.get('analysis'):
            elements.append(Paragraph("<b>Analysis:</b>", self.styles['SubsectionHeader']))
            elements.append(Paragraph(bias_data['analysis'], self.styles['CustomBody']))
        
        return elements
    
    def _create_additional_sections(self, data):
        """Create additional analysis sections"""
        elements = []
        
        # Transparency section (legacy)
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
        
        # Clickbait section (legacy)
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
            
            elements.append(Paragraph(assessment, style))
            elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    # ========================================================================
    # COVER PAGE & SUMMARY
    # ========================================================================
    
    def _create_cover_page(self, data):
        """Create PDF cover page"""
        elements = []
        
        # Title
        title = data.get('article', {}).get('title', 'News Analysis Report')
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        source = data.get('article', {}).get('source', 'Unknown Source')
        date = datetime.now().strftime("%B %d, %Y")
        subtitle = f"Analysis Report • {source} • {date}"
        elements.append(Paragraph(subtitle, self.styles['Subtitle']))
        elements.append(Spacer(1, 1*inch))
        
        # Trust score
        trust_score = data.get('trust_score', 0)
        
        score_drawing = Drawing(400, 150)
        
        # Circle background
        score_drawing.add(Circle(200, 75, 60, 
                                fillColor=colors.HexColor('#f3f4f6'),
                                strokeColor=None))
        
        # Score text
        score_drawing.add(String(200, 70, str(trust_score),
                                fontSize=48,
                                fillColor=colors.HexColor('#1e40af'),
                                textAnchor='middle'))
        score_drawing.add(String(200, 50, "/100",
                                fontSize=20,
                                fillColor=colors.HexColor('#6b7280'),
                                textAnchor='middle'))
        score_drawing.add(String(200, 20, "Trust Score",
                                fontSize=14,
                                fillColor=colors.HexColor('#1e293b'),
                                textAnchor='middle'))
        
        elements.append(score_drawing)
        elements.append(Spacer(1, 0.5*inch))
        
        # Add horizontal line
        elements.append(HRFlowable(width="100%", thickness=2, 
                                  color=colors.HexColor('#e5e7eb')))
        
        return elements
    
    def _create_executive_summary(self, data):
        """Create executive summary page"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Overall assessment
        trust_score = data.get('trust_score', 0)
        
        if trust_score >= 70:
            assessment = "This article demonstrates strong credibility across multiple factors. The source is reputable, content is well-verified, and presentation meets professional standards."
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
    
    def _create_footer(self):
        """Create PDF footer"""
        elements = []
        
        elements.append(Spacer(1, 0.5*inch))
        elements.append(HRFlowable(width="100%", thickness=1, 
                                  color=colors.HexColor('#e5e7eb')))
        elements.append(Spacer(1, 0.2*inch))
        
        footer_text = (
            "This analysis was generated by TruthLens, an AI-powered news credibility platform. "
            "While our analysis uses advanced algorithms and multiple verification methods, "
            "we recommend using your own judgment and consulting multiple sources for important decisions. "
            "Visit factsandfakes.ai for more information."
        )
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER
        )
        
        elements.append(Paragraph(footer_text, footer_style))
        
        return elements
    
    # ========================================================================
    # STYLES
    # ========================================================================
    
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
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=6,
            spaceAfter=6,
            leading=14
        ))
        
        # Success message style
        self.styles.add(ParagraphStyle(
            name='Success',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#065f46'),
            backColor=colors.HexColor('#d1fae5'),
            borderPadding=10,
            borderRadius=6
        ))
        
        # Info message style
        self.styles.add(ParagraphStyle(
            name='Info',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#1e40af'),
            backColor=colors.HexColor('#dbeafe'),
            borderPadding=10,
            borderRadius=6
        ))
        
        # Alert message style
        self.styles.add(ParagraphStyle(
            name='Alert',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#991b1b'),
            backColor=colors.HexColor('#fee2e2'),
            borderPadding=10,
            borderRadius=6
        ))
    
    def _add_page_number(self, canvas, doc):
        """Add page numbers to PDF"""
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#6b7280'))
        canvas.drawRightString(doc.pagesize[0] - 72, 30, text)
        canvas.restoreState()

# I did no harm and this file is not truncated.
