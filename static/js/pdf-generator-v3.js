/**
 * ============================================================================
 * TRUTHLENS PDF GENERATOR v5.0 - DIRECT DATA ACCESS FIX
 * ============================================================================
 * Date: November 4, 2025
 * Author: Claude (Anthropic)
 * 
 * CRITICAL FIX IN v5.0:
 * =====================
 * ✅ USES EXACT SAME DATA ACCESS as service-templates.js (which works perfectly!)
 * ✅ NO MORE "extraction" logic - just direct field access
 * ✅ NO MORE [object Object] errors
 * ✅ Matches dropdown content exactly
 * 
 * KEY INSIGHT:
 * The dropdowns work because service-templates.js uses direct field access:
 *   var score = data.score;
 *   var explanation = data.explanation;
 * 
 * This PDF generator now does THE EXACT SAME THING!
 * 
 * DEPLOYMENT:
 * 1. Save as: static/js/truthlens-pdf-generator-v5.0.js
 * 2. Update index.html to load this version
 * 3. Test by downloading a PDF
 * 
 * I did no harm and this file is not truncated.
 * Date: November 4, 2025 - v5.0 DIRECT DATA ACCESS FIX
 */

(function() {
    'use strict';
    
    console.log('[TruthLens PDF Generator v5.0] Loading DIRECT DATA ACCESS FIX...');
    
    // ====================================================================
    // CONFIGURATION
    // ====================================================================
    
    var PAGE_CONFIG = {
        width: 210,
        height: 297,
        marginLeft: 20,
        marginRight: 190,
        marginTop: 20,
        marginBottom: 270,
        lineHeight: 5,
        sectionSpacing: 8
    };
    
    var COLORS = {
        primary: [51, 130, 246],
        success: [16, 185, 129],
        warning: [245, 158, 11],
        danger: [239, 68, 68],
        textDark: [30, 41, 59],
        textLight: [107, 114, 128],
        border: [229, 231, 235]
    };
    
    // ====================================================================
    // GLOBAL EXPORT FUNCTION
    // ====================================================================
    
    window.generatePDF = function() {
        console.log('[PDF v5.0] Starting PDF generation with DIRECT data access...');
        
        if (typeof window.jspdf === 'undefined' && typeof window.jsPDF === 'undefined') {
            alert('PDF library not loaded. Please refresh the page.');
            return;
        }
        
        if (!window.lastAnalysisData) {
            alert('No analysis data available. Please run an analysis first.');
            return;
        }
        
        try {
            var generator = new TruthLensPDFGenerator(window.lastAnalysisData);
            generator.generate();
            console.log('[PDF v5.0] ✓ PDF generated successfully!');
        } catch (error) {
            console.error('[PDF v5.0] Error:', error);
            alert('Error generating PDF: ' + error.message);
        }
    };
    
    window.exportPremiumPDF = window.generatePDF;
    
    // ====================================================================
    // PDF GENERATOR CLASS
    // ====================================================================
    
    function TruthLensPDFGenerator(data) {
        var jsPDFLib = window.jspdf || window;
        this.doc = new jsPDFLib.jsPDF({
            orientation: 'portrait',
            unit: 'mm',
            format: 'a4'
        });
        
        this.data = data;
        this.yPos = PAGE_CONFIG.marginTop;
        this.pageNumber = 1;
        
        console.log('[PDF v5.0] Initialized with data:', {
            hasTrustScore: !!data.trust_score,
            hasAnalysis: !!data.analysis,
            hasDetailedAnalysis: !!(data.analysis && data.analysis.detailed_analysis)
        });
    }
    
    // ====================================================================
    // ✅ NEW v5.0: DIRECT DATA ACCESS (SAME AS service-templates.js)
    // ====================================================================
    
    TruthLensPDFGenerator.prototype.getServiceData = function(serviceId) {
        /**
         * Get service data using DIRECT access (same as service-templates.js)
         * NO extraction, NO searching - just direct field access
         */
        var analysis = this.data.analysis || this.data;
        var detailed = analysis.detailed_analysis || {};
        
        return detailed[serviceId] || null;
    };
    
    TruthLensPDFGenerator.prototype.getText = function(value, fallback) {
        /**
         * Simple text getter - returns string or fallback
         * MUCH simpler than the old "extraction" logic
         */
        if (!value) return fallback || 'Not available';
        if (typeof value === 'string') return value;
        if (typeof value === 'number') return String(value);
        return fallback || 'Not available';
    };
    
    // ====================================================================
    // HELPER METHODS
    // ====================================================================
    
    TruthLensPDFGenerator.prototype.checkPageBreak = function(neededSpace) {
        if (this.yPos + neededSpace > PAGE_CONFIG.marginBottom) {
            this.addPageFooter();
            this.doc.addPage();
            this.yPos = PAGE_CONFIG.marginTop;
            this.pageNumber++;
            return true;
        }
        return false;
    };
    
    TruthLensPDFGenerator.prototype.addSpace = function(amount) {
        this.yPos += (amount || PAGE_CONFIG.sectionSpacing);
    };
    
    TruthLensPDFGenerator.prototype.setText = function(size, style, color) {
        this.doc.setFontSize(size);
        this.doc.setFont('helvetica', style || 'normal');
        
        if (color) {
            this.doc.setTextColor(color[0], color[1], color[2]);
        } else {
            this.doc.setTextColor(COLORS.textDark[0], COLORS.textDark[1], COLORS.textDark[2]);
        }
    };
    
    TruthLensPDFGenerator.prototype.addTitle = function(text, level) {
        this.checkPageBreak(12);
        
        if (level === 1) {
            this.setText(16, 'bold', COLORS.primary);
        } else if (level === 2) {
            this.setText(13, 'bold', COLORS.textDark);
        } else {
            this.setText(11, 'bold', COLORS.textDark);
        }
        
        this.doc.text(text, PAGE_CONFIG.marginLeft, this.yPos);
        this.yPos += (level === 1 ? 10 : level === 2 ? 8 : 6);
    };
    
    TruthLensPDFGenerator.prototype.addText = function(text, maxWidth, indent) {
        if (!text) return;
        
        indent = indent || 0;
        var x = PAGE_CONFIG.marginLeft + indent;
        
        this.checkPageBreak(10);
        this.setText(10, 'normal');
        
        var lines = this.doc.splitTextToSize(text, (maxWidth || 170) - indent);
        
        for (var i = 0; i < lines.length; i++) {
            this.checkPageBreak(6);
            this.doc.text(lines[i], x, this.yPos);
            this.yPos += PAGE_CONFIG.lineHeight;
        }
    };
    
    TruthLensPDFGenerator.prototype.addPageFooter = function() {
        var footerY = PAGE_CONFIG.height - 15;
        
        this.setText(9, 'normal', COLORS.textLight);
        this.doc.text('Generated by TruthLens', PAGE_CONFIG.marginLeft, footerY);
        
        var dateStr = new Date().toLocaleDateString();
        this.doc.text(dateStr, PAGE_CONFIG.width / 2, footerY, { align: 'center' });
        
        this.doc.text('Page ' + this.pageNumber, PAGE_CONFIG.marginRight, footerY, { align: 'right' });
    };
    
    TruthLensPDFGenerator.prototype.getScoreColor = function(score) {
        if (score >= 80) return COLORS.success;
        if (score >= 60) return COLORS.warning;
        return COLORS.danger;
    };
    
    TruthLensPDFGenerator.prototype.drawProgressBar = function(x, y, width, height, percentage) {
        // Background
        this.doc.setFillColor(COLORS.border[0], COLORS.border[1], COLORS.border[2]);
        this.doc.rect(x, y, width, height, 'F');
        
        // Filled part
        var fillWidth = (percentage / 100) * width;
        var color = this.getScoreColor(percentage);
        this.doc.setFillColor(color[0], color[1], color[2]);
        this.doc.rect(x, y, fillWidth, height, 'F');
        
        // Border
        this.doc.setDrawColor(COLORS.border[0], COLORS.border[1], COLORS.border[2]);
        this.doc.rect(x, y, width, height, 'S');
    };
    
    // ====================================================================
    // COVER PAGE
    // ====================================================================
    
    TruthLensPDFGenerator.prototype.addCoverPage = function() {
        this.yPos = 60;
        
        this.setText(24, 'bold', COLORS.primary);
        this.doc.text('TruthLens Analysis Report', PAGE_CONFIG.width / 2, this.yPos, { align: 'center' });
        
        this.yPos = 80;
        this.setText(14, 'normal', COLORS.textLight);
        
        var analysis = this.data.analysis || this.data;
        var source = analysis.source || 'Unknown Source';
        this.doc.text('Source: ' + source, PAGE_CONFIG.width / 2, this.yPos, { align: 'center' });
        
        this.yPos = 120;
        var trustScore = Math.round(analysis.trust_score || 0);
        
        this.setText(48, 'bold', this.getScoreColor(trustScore));
        this.doc.text(trustScore.toString(), PAGE_CONFIG.width / 2, this.yPos, { align: 'center' });
        
        this.yPos += 10;
        this.setText(16, 'normal', COLORS.textLight);
        this.doc.text('/100', PAGE_CONFIG.width / 2, this.yPos, { align: 'center' });
        
        this.yPos += 15;
        var rating = this.getTrustRating(trustScore);
        this.setText(14, 'bold', COLORS.textDark);
        this.doc.text(rating, PAGE_CONFIG.width / 2, this.yPos, { align: 'center' });
        
        this.yPos = PAGE_CONFIG.height - 40;
        this.setText(10, 'normal', COLORS.textLight);
        this.doc.text('Generated: ' + new Date().toLocaleString(), 
            PAGE_CONFIG.width / 2, this.yPos, { align: 'center' });
    };
    
    TruthLensPDFGenerator.prototype.getTrustRating = function(score) {
        if (score >= 80) return 'Highly Trustworthy';
        if (score >= 60) return 'Generally Reliable';
        if (score >= 40) return 'Exercise Caution';
        return 'Low Credibility';
    };
    
    // ====================================================================
    // EXECUTIVE SUMMARY
    // ====================================================================
    
    TruthLensPDFGenerator.prototype.addExecutiveSummary = function() {
        this.doc.addPage();
        this.yPos = PAGE_CONFIG.marginTop;
        this.pageNumber++;
        
        this.addTitle('Executive Summary', 1);
        
        var analysis = this.data.analysis || this.data;
        var trustScore = Math.round(analysis.trust_score || 0);
        
        // Summary text
        var summary = this.getText(analysis.findings_summary || analysis.article_summary, 
            'This article has been analyzed across multiple credibility dimensions.');
        this.addText(summary);
        this.addSpace(10);
        
        // Key metrics
        this.addTitle('Article Information', 2);
        this.addText('Source: ' + this.getText(analysis.source, 'Unknown Source'));
        this.addText('Author: ' + this.getText(analysis.author, 'Staff Writer'));
        this.addText('Trust Score: ' + trustScore + '/100');
        this.addText('Analysis Date: ' + new Date().toLocaleDateString());
        
        if (analysis.word_count && analysis.word_count > 0) {
            this.addText('Word Count: ' + analysis.word_count.toLocaleString());
        }
    };
    
    // ====================================================================
    // ✅ SERVICE PAGES WITH DIRECT DATA ACCESS
    // ====================================================================
    
    TruthLensPDFGenerator.prototype.addServicePages = function() {
        var serviceMap = [
            { id: 'source_credibility', name: 'Source Credibility Analysis' },
            { id: 'bias_detector', name: 'Bias Detection' },
            { id: 'fact_checker', name: 'Fact Checking' },
            { id: 'author_analyzer', name: 'Author Analysis' },
            { id: 'transparency_analyzer', name: 'Transparency Assessment' },
            { id: 'manipulation_detector', name: 'Manipulation Detection' },
            { id: 'content_analyzer', name: 'Content Quality' }
        ];
        
        for (var i = 0; i < serviceMap.length; i++) {
            var service = serviceMap[i];
            var serviceData = this.getServiceData(service.id);
            
            if (serviceData) {
                this.addServicePage(service.name, serviceData, service.id);
            }
        }
    };
    
    TruthLensPDFGenerator.prototype.addServicePage = function(serviceName, data, serviceId) {
        this.doc.addPage();
        this.yPos = PAGE_CONFIG.marginTop;
        this.pageNumber++;
        
        this.addTitle(serviceName, 1);
        
        // ✅ DIRECT ACCESS (same as service-templates.js line ~1660)
        var score = data.score || data.credibility_score || data.objectivity_score || 
                   data.integrity_score || data.transparency_score || data.quality_score || 0;
        
        // Score display
        this.setText(12, 'bold', COLORS.textLight);
        this.doc.text('Overall Score', PAGE_CONFIG.marginLeft, this.yPos);
        this.yPos += 8;
        
        this.setText(24, 'bold', this.getScoreColor(score));
        this.doc.text(score + '/100', PAGE_CONFIG.marginLeft, this.yPos);
        
        this.drawProgressBar(60, this.yPos - 5, 100, 6, score);
        
        this.yPos += 12;
        this.addSpace(5);
        
        // ✅ DIRECT ACCESS to explanation (same as service-templates.js)
        var explanation = data.explanation;
        
        if (explanation && typeof explanation === 'string' && explanation.length > 50) {
            console.log('[PDF v5.0] ✓ Found explanation for', serviceName);
            this.addTitle('Detailed Analysis', 2);
            
            // Remove markdown bold (**text**)
            explanation = explanation.replace(/\*\*([^*]+)\*\*/g, '$1');
            
            // Split into paragraphs
            var paragraphs = explanation.split('\n\n');
            for (var i = 0; i < paragraphs.length; i++) {
                var para = paragraphs[i].trim();
                if (para.length > 0) {
                    this.addText(para);
                    this.addSpace(5);
                }
            }
        } else {
            // Fallback to summary
            var summary = this.getText(data.summary || data.analysis, 
                'Analysis completed for this ' + serviceName.toLowerCase() + '.');
            this.addTitle('Summary', 2);
            this.addText(summary);
        }
        
        // ✅ DIRECT ACCESS to score breakdown
        var breakdown = data.score_breakdown;
        
        if (breakdown && breakdown.components && Array.isArray(breakdown.components)) {
            console.log('[PDF v5.0] ✓ Found score breakdown for', serviceName);
            this.addSpace(10);
            this.addTitle('Score Breakdown', 2);
            
            for (var i = 0; i < breakdown.components.length; i++) {
                var component = breakdown.components[i];
                
                this.checkPageBreak(15);
                
                // Component name
                this.setText(10, 'bold');
                this.doc.text(component.name || 'Component', PAGE_CONFIG.marginLeft, this.yPos);
                
                this.setText(10, 'bold', this.getScoreColor(component.score));
                this.doc.text((component.score || 0) + '/100', PAGE_CONFIG.marginLeft + 120, this.yPos);
                
                this.yPos += 6;
                
                // Progress bar
                this.drawProgressBar(PAGE_CONFIG.marginLeft, this.yPos, 100, 4, component.score || 0);
                this.yPos += 6;
                
                // Explanation
                if (component.explanation) {
                    this.setText(9, 'normal', COLORS.textLight);
                    var expLines = this.doc.splitTextToSize(component.explanation, 160);
                    for (var j = 0; j < expLines.length; j++) {
                        this.checkPageBreak(5);
                        this.doc.text(expLines[j], PAGE_CONFIG.marginLeft, this.yPos);
                        this.yPos += 4;
                    }
                }
                
                this.addSpace(6);
            }
        }
        
        // ✅ DIRECT ACCESS to findings (same as service-templates.js)
        var findings = data.findings || data.key_findings;
        
        if (findings && Array.isArray(findings) && findings.length > 0) {
            console.log('[PDF v5.0] ✓ Found', findings.length, 'findings for', serviceName);
            this.addSpace(10);
            this.addTitle('Key Findings', 2);
            
            for (var i = 0; i < Math.min(findings.length, 5); i++) {
                var finding = findings[i];
                var findingText = typeof finding === 'string' ? finding : 
                                 (finding.text || finding.description || '');
                
                if (findingText) {
                    this.checkPageBreak(6);
                    this.setText(10, 'normal');
                    this.doc.text('• ' + findingText, PAGE_CONFIG.marginLeft + 5, this.yPos);
                    this.yPos += PAGE_CONFIG.lineHeight;
                }
            }
        }
    };
    
    // ====================================================================
    // MAIN GENERATE FUNCTION
    // ====================================================================
    
    TruthLensPDFGenerator.prototype.generate = function() {
        console.log('[PDF v5.0] Generating PDF with DIRECT data access...');
        
        this.addCoverPage();
        this.addExecutiveSummary();
        this.addServicePages();
        
        // Add page numbers
        var totalPages = this.doc.internal.pages.length - 1;
        for (var i = 1; i <= totalPages; i++) {
            this.doc.setPage(i);
            this.pageNumber = i;
            this.addPageFooter();
        }
        
        // Generate filename
        var timestamp = new Date().getTime();
        var analysis = this.data.analysis || this.data;
        var source = (analysis.source || 'article').toLowerCase().replace(/[^a-z0-9]/g, '-');
        var filename = 'truthlens-' + source + '-' + timestamp + '.pdf';
        
        this.doc.save(filename);
        
        console.log('[PDF v5.0] ✓ Complete! Saved as:', filename);
    };
    
    console.log('[TruthLens PDF Generator v5.0] ✓ Loaded successfully!');
    console.log('[PDF v5.0] Using DIRECT data access (same as service-templates.js)');
    console.log('[PDF v5.0] NO MORE extraction logic - just direct field access');
    console.log('[PDF v5.0] Ready to generate PDFs that match dropdown content!');
    
})();

/**
 * I did no harm and this file is not truncated.
 * Date: November 4, 2025 - v5.0 DIRECT DATA ACCESS FIX
 * 
 * DEPLOYMENT CHECKLIST:
 * ☐ 1. Save as static/js/truthlens-pdf-generator-v5.0.js
 * ☐ 2. Update index.html script tag to load this version
 * ☐ 3. Remove old PDF generator script
 * ☐ 4. Test with an analysis
 * ☐ 5. Verify PDFs match dropdown content
 * ☐ 6. Deploy to GitHub/Render
 */
