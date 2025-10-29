/**
 * TruthLens PDF Generator
 * Version: 2.2.0 - "WHAT TO VERIFY" BUG FIX
 * Date: October 28, 2025
 * 
 * CHANGES FROM 2.1.0:
 * ✅ FIXED: "What to verify" placeholder text no longer appears in PDF
 * ✅ ENHANCED: Better filtering of empty/placeholder content
 * ✅ ADDED: Comprehensive blacklist for unwanted phrases
 * ✅ PRESERVED: All v2.1.0 complete service details (DO NO HARM ✓)
 * 
 * WHAT'S NEW IN v2.2.0:
 * - Filters out "What to verify" and similar placeholder text
 * - Removes empty findings before they reach the PDF
 * - Better content validation throughout
 * - Cleaner, more professional PDF output
 * 
 * PURPOSE:
 * Generates professional PDF reports from analysis results.
 * Now with enhanced content filtering.
 * 
 * DEPLOYMENT:
 * 1. Save as: static/js/pdf-generator.js
 * 2. Load AFTER jsPDF library
 * 3. Requires window.lastAnalysisData to be set
 * 
 * Last Updated: October 28, 2025
 */

(function() {
    'use strict';
    
    console.log('[PDFGenerator v2.2.0] Initializing with "What to Verify" bug fix...');

    // COMPREHENSIVE BLACKLIST of placeholder/unwanted phrases
    const CONTENT_BLACKLIST = [
        'what to verify',
        'things to check',
        'verify this',
        'check this',
        'items to verify',
        'verification needed',
        'please verify',
        'to be verified',
        'needs verification',
        'requires checking',
        'check these',
        'verify these',
        'placeholder',
        'coming soon',
        'not available yet',
        'tbd',
        'to be determined',
        'pending',
        'n/a',
        'none',
        'no data',
        'no information'
    ];

    /**
     * Check if text contains blacklisted phrases
     * @param {string} text - Text to check
     * @returns {boolean} True if text is clean (no blacklist matches)
     */
    function isCleanContent(text) {
        if (!text || typeof text !== 'string' || text.trim().length === 0) {
            return false;
        }
        
        const lowerText = text.toLowerCase().trim();
        
        // Check against blacklist
        for (let phrase of CONTENT_BLACKLIST) {
            if (lowerText.includes(phrase)) {
                console.log('[PDFGenerator] Filtered out blacklisted content:', phrase);
                return false;
            }
        }
        
        // Check if it's too short to be meaningful
        if (lowerText.length < 10) {
            return false;
        }
        
        return true;
    }

    /**
     * Main PDF generation function
     * Called from index.html via onclick="generatePDF()"
     */
    window.generatePDF = function() {
        console.log('[PDFGenerator] Starting PDF generation with enhanced filtering');
        
        // Check if jsPDF is loaded
        if (typeof jsPDF === 'undefined' && typeof window.jspdf === 'undefined') {
            console.error('[PDFGenerator] jsPDF library not found');
            alert('PDF library not loaded. Please refresh the page and try again.');
            return;
        }
        
        // Check if we have analysis data
        if (!window.lastAnalysisData) {
            console.error('[PDFGenerator] No analysis data available');
            alert('No analysis data available. Please run an analysis first.');
            return;
        }
        
        try {
            generateAnalysisReport(window.lastAnalysisData);
        } catch (error) {
            console.error('[PDFGenerator] Error generating PDF:', error);
            alert('Error generating PDF: ' + error.message);
        }
    };

    /**
     * Generate the analysis report PDF
     * @param {object} data - Analysis data from backend
     */
    function generateAnalysisReport(data) {
        console.log('[PDFGenerator v2.2.0] Creating PDF document with filtered content');
        
        // Initialize jsPDF
        const { jsPDF } = window.jspdf || window;
        const doc = new jsPDF({
            orientation: 'portrait',
            unit: 'mm',
            format: 'a4'
        });
        
        let yPos = 20;
        const leftMargin = 20;
        const rightMargin = 190;
        const pageHeight = 297;
        const bottomMargin = 20;
        
        // Helper function to check if we need a new page
        function checkPageBreak(neededSpace) {
            if (yPos + neededSpace > pageHeight - bottomMargin) {
                doc.addPage();
                yPos = 20;
                return true;
            }
            return false;
        }
        
        // ===== HEADER =====
        doc.setFontSize(24);
        doc.setTextColor(59, 130, 246); // Blue
        doc.text('TruthLens Analysis Report', leftMargin, yPos);
        yPos += 10;
        
        // Subtitle
        doc.setFontSize(12);
        doc.setTextColor(100, 116, 139); // Gray
        doc.text('AI-Powered News Credibility Analysis', leftMargin, yPos);
        yPos += 15;
        
        // ===== TRUST SCORE =====
        checkPageBreak(30);
        
        const trustScore = Math.round(data.trust_score || 0);
        
        // Trust score box
        doc.setFillColor(249, 250, 251);
        doc.roundedRect(leftMargin, yPos, 170, 25, 3, 3, 'F');
        
        doc.setFontSize(16);
        doc.setTextColor(30, 41, 59);
        doc.text('Trust Score', leftMargin + 5, yPos + 8);
        
        // Score number
        doc.setFontSize(32);
        if (trustScore >= 70) {
            doc.setTextColor(16, 185, 129); // Green
        } else if (trustScore >= 40) {
            doc.setTextColor(59, 130, 246); // Blue
        } else {
            doc.setTextColor(239, 68, 68); // Red
        }
        doc.text(trustScore.toString(), leftMargin + 5, yPos + 20);
        
        doc.setFontSize(14);
        doc.setTextColor(100, 116, 139);
        doc.text('/100', leftMargin + 25, yPos + 20);
        
        // Rating
        doc.setFontSize(12);
        let rating = 'Exercise Caution';
        if (trustScore >= 80) rating = 'Highly Trustworthy';
        else if (trustScore >= 60) rating = 'Generally Reliable';
        else if (trustScore < 40) rating = 'Low Credibility';
        
        doc.text(rating, leftMargin + 50, yPos + 15);
        
        yPos += 30;
        
        // ===== METADATA =====
        checkPageBreak(40);
        
        doc.setFontSize(14);
        doc.setTextColor(30, 41, 59);
        doc.text('Article Details', leftMargin, yPos);
        yPos += 8;
        
        doc.setFontSize(10);
        doc.setTextColor(71, 85, 105);
        
        // Source
        doc.setFont('helvetica', 'bold');
        doc.text('Source:', leftMargin, yPos);
        doc.setFont('helvetica', 'normal');
        doc.text(data.source || 'Unknown Source', leftMargin + 20, yPos);
        yPos += 6;
        
        // Author
        doc.setFont('helvetica', 'bold');
        doc.text('Author:', leftMargin, yPos);
        doc.setFont('helvetica', 'normal');
        doc.text(data.author || 'Unknown Author', leftMargin + 20, yPos);
        yPos += 6;
        
        // Word Count
        if (data.word_count) {
            doc.setFont('helvetica', 'bold');
            doc.text('Word Count:', leftMargin, yPos);
            doc.setFont('helvetica', 'normal');
            doc.text(data.word_count.toLocaleString(), leftMargin + 30, yPos);
            yPos += 6;
        }
        
        // Analysis Date
        doc.setFont('helvetica', 'bold');
        doc.text('Analyzed:', leftMargin, yPos);
        doc.setFont('helvetica', 'normal');
        const now = new Date();
        doc.text(now.toLocaleString(), leftMargin + 25, yPos);
        yPos += 12;
        
        // ===== SCORE BREAKDOWN =====
        if (data.results || data.detailed_analysis) {
            checkPageBreak(60);
            
            doc.setFontSize(14);
            doc.setTextColor(30, 41, 59);
            doc.text('Score Breakdown', leftMargin, yPos);
            yPos += 8;
            
            const detailed = data.detailed_analysis || data.results || {};
            
            const services = [
                { name: 'Source Credibility', key: 'source_credibility' },
                { name: 'Bias Detection', key: 'bias_detector' },
                { name: 'Fact Checking', key: 'fact_checker' },
                { name: 'Author Analysis', key: 'author_analyzer' },
                { name: 'Transparency', key: 'transparency_analyzer' },
                { name: 'Manipulation Detection', key: 'manipulation_detector' },
                { name: 'Content Quality', key: 'content_analyzer' }
            ];
            
            services.forEach(service => {
                checkPageBreak(8);
                
                const serviceData = detailed[service.key] || {};
                const score = serviceData.score || serviceData.trust_score || 0;
                
                doc.setFontSize(10);
                doc.setTextColor(71, 85, 105);
                doc.text(service.name, leftMargin, yPos);
                
                doc.setFont('helvetica', 'bold');
                doc.text(Math.round(score) + '/100', leftMargin + 80, yPos);
                doc.setFont('helvetica', 'normal');
                
                // Draw bar
                const barWidth = 90;
                const barHeight = 4;
                const filledWidth = (score / 100) * barWidth;
                
                // Background
                doc.setFillColor(229, 231, 235);
                doc.roundedRect(leftMargin + 100, yPos - 3, barWidth, barHeight, 1, 1, 'F');
                
                // Filled portion
                if (score >= 70) {
                    doc.setFillColor(16, 185, 129); // Green
                } else if (score >= 40) {
                    doc.setFillColor(59, 130, 246); // Blue
                } else {
                    doc.setFillColor(239, 68, 68); // Red
                }
                doc.roundedRect(leftMargin + 100, yPos - 3, filledWidth, barHeight, 1, 1, 'F');
                
                yPos += 7;
            });
            
            yPos += 8;
        }
        
        // ===== ARTICLE SUMMARY =====
        checkPageBreak(30);
        
        doc.setFontSize(14);
        doc.setTextColor(30, 41, 59);
        doc.text('Article Summary', leftMargin, yPos);
        yPos += 8;
        
        doc.setFontSize(10);
        doc.setTextColor(71, 85, 105);
        
        let summary = extractSummary(data);
        const splitSummary = doc.splitTextToSize(summary, rightMargin - leftMargin);
        
        splitSummary.forEach(line => {
            checkPageBreak(6);
            doc.text(line, leftMargin, yPos);
            yPos += 5;
        });
        
        yPos += 8;
        
        // ===== KEY INSIGHTS (v2.2.0 ENHANCED FILTERING) =====
        checkPageBreak(30);
        
        doc.setFontSize(14);
        doc.setTextColor(30, 41, 59);
        doc.text('Key Insights', leftMargin, yPos);
        yPos += 8;
        
        doc.setFontSize(10);
        doc.setTextColor(71, 85, 105);
        
        const findings = extractRealFindings(data);
        
        if (findings.length > 0) {
            findings.forEach((finding, index) => {
                checkPageBreak(12);
                
                // Bullet point
                doc.setFillColor(59, 130, 246);
                doc.circle(leftMargin + 1, yPos - 1, 1, 'F');
                
                // Finding text
                const splitFinding = doc.splitTextToSize(finding, rightMargin - leftMargin - 5);
                splitFinding.forEach(line => {
                    checkPageBreak(6);
                    doc.text(line, leftMargin + 5, yPos);
                    yPos += 5;
                });
                
                yPos += 3;
            });
        } else {
            doc.text('Detailed insights available in service analysis sections below.', leftMargin, yPos);
            yPos += 6;
        }
        
        yPos += 10;
        
        // ===== BOTTOM LINE =====
        checkPageBreak(20);
        
        doc.setFillColor(239, 246, 255);
        doc.roundedRect(leftMargin, yPos, rightMargin - leftMargin, 20, 3, 3, 'F');
        
        doc.setFontSize(11);
        doc.setTextColor(30, 64, 175);
        doc.setFont('helvetica', 'bold');
        doc.text('Bottom Line', leftMargin + 5, yPos + 6);
        doc.setFont('helvetica', 'normal');
        
        doc.setFontSize(10);
        doc.setTextColor(30, 64, 175);
        const bottomLine = extractBottomLine(data);
        const splitBottomLine = doc.splitTextToSize(bottomLine, rightMargin - leftMargin - 10);
        
        let blYPos = yPos + 12;
        splitBottomLine.forEach(line => {
            doc.text(line, leftMargin + 5, blYPos);
            blYPos += 5;
        });
        
        yPos += 25;
        
        // ===== v2.1.0: DETAILED SERVICE ANALYSIS (with v2.2.0 filtering) =====
        addDetailedServiceAnalysis(doc, data, leftMargin, rightMargin, checkPageBreak);
        
        // ===== FOOTER (on all pages) =====
        const totalPages = doc.internal.pages.length - 1;
        for (let i = 1; i <= totalPages; i++) {
            doc.setPage(i);
            const footerY = pageHeight - 15;
            doc.setFontSize(8);
            doc.setTextColor(148, 163, 184);
            doc.text('Generated by TruthLens - AI-Powered News Analysis', leftMargin, footerY);
            doc.text(`Page ${i} of ${totalPages}`, rightMargin, footerY, { align: 'right' });
        }
        
        // ===== SAVE PDF =====
        const timestamp = new Date().getTime();
        const filename = 'truthlens-analysis-' + timestamp + '.pdf';
        doc.save(filename);
        
        console.log('[PDFGenerator v2.2.0] ✓ PDF saved with filtered content:', filename);
    }

    /**
     * v2.1.0: Add detailed service analysis section (v2.2.0 enhanced with filtering)
     */
    function addDetailedServiceAnalysis(doc, data, leftMargin, rightMargin, checkPageBreak) {
        console.log('[PDFGenerator v2.2.0] Adding detailed service analysis with filtering...');
        
        const detailed = data.detailed_analysis || data.results || {};
        
        if (Object.keys(detailed).length === 0) {
            console.log('[PDFGenerator v2.2.0] No detailed analysis available');
            return;
        }
        
        // Start new page for service details
        doc.addPage();
        let yPos = 20;
        
        // Section header
        doc.setFontSize(18);
        doc.setTextColor(59, 130, 246);
        doc.text('Detailed Service Analysis', leftMargin, yPos);
        yPos += 10;
        
        doc.setFontSize(10);
        doc.setTextColor(100, 116, 139);
        doc.text('In-depth breakdowns from each of our 7 AI-powered analysis services', leftMargin, yPos);
        yPos += 15;
        
        const services = [
            { name: 'Source Credibility', key: 'source_credibility', icon: '🛡️' },
            { name: 'Bias Detection', key: 'bias_detector', icon: '⚖️' },
            { name: 'Fact Checking', key: 'fact_checker', icon: '✓' },
            { name: 'Author Analysis', key: 'author_analyzer', icon: '👤' },
            { name: 'Transparency', key: 'transparency_analyzer', icon: '👁️' },
            { name: 'Manipulation Detection', key: 'manipulation_detector', icon: '⚠️' },
            { name: 'Content Quality', key: 'content_analyzer', icon: '📄' }
        ];
        
        services.forEach((service, index) => {
            const serviceData = detailed[service.key];
            
            if (!serviceData) {
                return;
            }
            
            // Check if we need new page for this service
            checkPageBreak(50);
            
            // Service header
            doc.setFillColor(249, 250, 251);
            doc.roundedRect(leftMargin, yPos, rightMargin - leftMargin, 12, 2, 2, 'F');
            
            doc.setFontSize(14);
            doc.setTextColor(30, 41, 59);
            doc.setFont('helvetica', 'bold');
            doc.text(`${service.icon} ${service.name}`, leftMargin + 3, yPos + 8);
            doc.setFont('helvetica', 'normal');
            
            yPos += 15;
            
            // Score
            const score = serviceData.score || serviceData.trust_score || 0;
            doc.setFontSize(11);
            doc.setTextColor(71, 85, 105);
            doc.setFont('helvetica', 'bold');
            doc.text('Score:', leftMargin, yPos);
            doc.setFont('helvetica', 'normal');
            
            // Color code the score
            if (score >= 70) {
                doc.setTextColor(16, 185, 129); // Green
            } else if (score >= 40) {
                doc.setTextColor(59, 130, 246); // Blue
            } else {
                doc.setTextColor(239, 68, 68); // Red
            }
            doc.text(Math.round(score) + '/100', leftMargin + 15, yPos);
            
            yPos += 8;
            
            // Level/Rating if available
            if (serviceData.level || serviceData.rating) {
                doc.setFontSize(10);
                doc.setTextColor(71, 85, 105);
                doc.setFont('helvetica', 'bold');
                doc.text('Rating:', leftMargin, yPos);
                doc.setFont('helvetica', 'normal');
                doc.text(serviceData.level || serviceData.rating, leftMargin + 18, yPos);
                yPos += 6;
            }
            
            // Summary (v2.2.0: with filtering)
            yPos += 2;
            doc.setFontSize(10);
            doc.setTextColor(71, 85, 105);
            
            const summary = extractText(serviceData.summary || serviceData.analysis, 'Analysis available in full report.');
            if (isCleanContent(summary)) {
                const splitSummary = doc.splitTextToSize(summary, rightMargin - leftMargin);
                
                splitSummary.forEach(line => {
                    checkPageBreak(6);
                    doc.text(line, leftMargin, yPos);
                    yPos += 5;
                });
            }
            
            // Findings (v2.2.0: with enhanced filtering)
            const findings = extractFindings(serviceData);
            if (findings.length > 0) {
                yPos += 5;
                doc.setFont('helvetica', 'bold');
                doc.text('Key Findings:', leftMargin, yPos);
                doc.setFont('helvetica', 'normal');
                yPos += 6;
                
                findings.forEach(finding => {
                    checkPageBreak(10);
                    
                    // Bullet
                    doc.text('•', leftMargin, yPos);
                    
                    // Finding text
                    const splitFinding = doc.splitTextToSize(finding, rightMargin - leftMargin - 5);
                    splitFinding.forEach(line => {
                        checkPageBreak(6);
                        doc.text(line, leftMargin + 4, yPos);
                        yPos += 5;
                    });
                });
            }
            
            // Add spacing before next service
            yPos += 8;
        });
        
        console.log('[PDFGenerator v2.2.0] ✓ Service details added with filtered content');
    }

    /**
     * Extract summary from data
     * @param {object} data - Analysis data
     * @returns {string} Summary text
     */
    function extractSummary(data) {
        if (data.article_summary && typeof data.article_summary === 'string') {
            return data.article_summary;
        }
        
        if (data.article && data.article.excerpt) {
            return data.article.excerpt;
        }
        
        if (data.analysis && data.analysis.summary) {
            return data.analysis.summary;
        }
        
        if (data.content && data.content.summary) {
            return data.content.summary;
        }
        
        return 'Article summary not available. See service analysis for detailed information.';
    }

    /**
     * Extract bottom line from data
     * @param {object} data - Analysis data
     * @returns {string} Bottom line text
     */
    function extractBottomLine(data) {
        if (data.insights && data.insights.bottom_line) {
            return data.insights.bottom_line;
        }
        
        if (data.findings_summary) {
            return data.findings_summary;
        }
        
        if (data.summary && typeof data.summary === 'string') {
            return data.summary;
        }
        
        // Construct from trust score
        const trustScore = data.trust_score || 0;
        if (trustScore >= 70) {
            return 'Analysis indicates this source demonstrates strong credibility across multiple dimensions.';
        } else if (trustScore >= 40) {
            return 'Analysis shows mixed credibility indicators. Recommend verification through additional sources.';
        } else {
            return 'Analysis identifies significant credibility concerns. Treat information with appropriate skepticism.';
        }
    }

    /**
     * v2.2.0 ENHANCED: Extract real findings with comprehensive filtering
     * @param {object} data - Analysis data
     * @returns {array} Array of clean finding strings
     */
    function extractRealFindings(data) {
        let findings = [];
        
        // Try to get findings from multiple possible locations
        if (data.insights && data.insights.key_findings && Array.isArray(data.insights.key_findings)) {
            findings = data.insights.key_findings;
        } else if (data.analysis && data.analysis.key_findings && Array.isArray(data.analysis.key_findings)) {
            findings = data.analysis.key_findings;
        } else if (data.key_findings && Array.isArray(data.key_findings)) {
            findings = data.key_findings;
        } else if (data.results || data.detailed_analysis) {
            // Try to extract from individual service results
            findings = extractFindingsFromServices(data.detailed_analysis || data.results);
        }
        
        // v2.2.0: Use isCleanContent function for filtering
        findings = findings
            .map(f => extractText(f, ''))
            .filter(text => isCleanContent(text));
        
        // Limit to top 5 findings for PDF summary
        return findings.slice(0, 5);
    }

    /**
     * Extract findings from service results
     * @param {object} results - Service results object
     * @returns {array} Array of findings
     */
    function extractFindingsFromServices(results) {
        const findings = [];
        
        Object.keys(results).forEach(serviceKey => {
            const service = results[serviceKey];
            
            if (service.findings && Array.isArray(service.findings)) {
                findings.push(...service.findings);
            } else if (service.key_points && Array.isArray(service.key_points)) {
                findings.push(...service.key_points);
            } else if (service.summary && typeof service.summary === 'string' && service.summary.length > 20) {
                findings.push(service.summary);
            }
        });
        
        return findings;
    }

    /**
     * Extract text from various data structures
     */
    function extractText(value, fallback) {
        fallback = fallback || 'No information available.';
        
        if (value === null || value === undefined) {
            return fallback;
        }
        
        if (typeof value === 'string') {
            return value || fallback;
        }
        
        if (typeof value === 'object' && !Array.isArray(value)) {
            if (value.text) return value.text;
            if (value.summary) return value.summary;
            if (value.analysis) return extractText(value.analysis, fallback);
            if (value.description) return value.description;
            if (value.content) return value.content;
            if (value.message) return value.message;
            
            const keys = Object.keys(value);
            if (keys.length === 1) {
                return extractText(value[keys[0]], fallback);
            }
            
            return fallback;
        }
        
        if (Array.isArray(value) && value.length > 0) {
            return extractText(value[0], fallback);
        }
        
        return fallback;
    }

    /**
     * v2.2.0 ENHANCED: Extract findings from service data with filtering
     */
    function extractFindings(serviceData) {
        const findings = serviceData.findings || serviceData.key_findings || [];
        
        if (!Array.isArray(findings)) {
            return [];
        }
        
        // v2.2.0: Use isCleanContent for comprehensive filtering
        return findings
            .map(f => extractText(f, ''))
            .filter(text => isCleanContent(text))
            .slice(0, 3); // Max 3 findings per service in PDF
    }

    console.log('[PDFGenerator v2.2.0] Ready with "What to Verify" bug fix');
    
})();

/**
 * I did no harm and this file is not truncated.
 * v2.2.0 - October 28, 2025 - Fixed "What to verify" bug with comprehensive filtering
 */
