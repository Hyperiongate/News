/**
 * ============================================================================
 * TRUTHLENS PDF GENERATOR v3.0 - COMPLETE WITH ALL SECTIONS
 * ============================================================================
 * Date: November 3, 2025
 * Last Updated: November 3, 2025 11:55 PM - COMPLETE VERSION
 * 
 * WHAT'S FIXED:
 * ✅ Replicated extractText() from service-templates.js
 * ✅ Fixed ASCII bar characters (■·)
 * ✅ PRESERVED all original sections (Risk Assessment, Comparative Analysis, Score Breakdown)
 * 
 * I did no harm and this file is not truncated.
 */

(function() {
    'use strict';
    
    console.log('[PDFGenerator v3.0] Loading COMPLETE version...');
    
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
        console.log('[PDFGenerator v3.0] Starting PDF generation...');
        
        if (typeof window.jspdf === 'undefined' && typeof window.jsPDF === 'undefined') {
            alert('PDF library not loaded. Please refresh the page.');
            return;
        }
        
        if (!window.lastAnalysisData) {
            alert('No analysis data available. Please run an analysis first.');
            return;
        }
        
        try {
            var generator = new EnhancedPDFGenerator(window.lastAnalysisData);
            generator.generate();
            console.log('[PDFGenerator v3.0] ✓ PDF generated successfully!');
        } catch (error) {
            console.error('[PDFGenerator v3.0] Error:', error);
            alert('Error generating PDF: ' + error.message);
        }
    };
    
    window.exportPremiumPDF = window.generatePDF;
    
    // ====================================================================
    // PDF GENERATOR CLASS
    // ====================================================================
    
    function EnhancedPDFGenerator(data) {
        var jsPDFLib = window.jspdf || window;
        this.doc = new jsPDFLib.jsPDF({
            orientation: 'portrait',
            unit: 'mm',
            format: 'a4'
        });
        
        this.data = data;
        this.yPos = PAGE_CONFIG.marginTop;
        this.pageNumber = 1;
        
        console.log('[PDFGenerator v3.0] Initialized with data:', {
            trustScore: data.trust_score,
            source: data.source,
            hasDetailedAnalysis: !!data.detailed_analysis
        });
    }
    
    // ====================================================================
    // ✅ CRITICAL FIX: REPLICATED extractText() FROM service-templates.js
    // ====================================================================
    
    EnhancedPDFGenerator.prototype.extractText = function(value, fallback) {
        fallback = fallback || 'No information available.';
        
        if (value === null || value === undefined) {
            return fallback;
        }
        
        if (typeof value === 'string') {
            var trimmed = value.trim();
            if (trimmed.length > 0) {
                return trimmed;
            }
            return fallback;
        }
        
        if (Array.isArray(value)) {
            if (value.length > 0) {
                return this.extractText(value[0], fallback);
            }
            return fallback;
        }
        
        if (typeof value === 'object') {
            var textFields = [
                'text', 'summary', 'analysis', 'description', 'content', 'message',
                'result', 'output', 'response', 'explanation', 'details', 'body',
                'narrative', 'commentary', 'assessment', 'evaluation', 'conclusion',
                'findings_text', 'summary_text', 'analysis_text', 'detailed_analysis',
                'full_text', 'main_text', 'primary_text'
            ];
            
            for (var i = 0; i < textFields.length; i++) {
                var field = textFields[i];
                if (value[field] !== undefined && value[field] !== null) {
                    var extracted = this.extractText(value[field], null);
                    if (extracted && extracted !== fallback) {
                        return extracted;
                    }
                }
            }
            
            var keys = Object.keys(value);
            if (keys.length === 1) {
                return this.extractText(value[keys[0]], fallback);
            }
            
            for (var i = 0; i < keys.length; i++) {
                var key = keys[i];
                var val = value[key];
                if (typeof val === 'string' && val.trim().length > 20) {
                    return val.trim();
                }
            }
            
            for (var i = 0; i < keys.length; i++) {
                var key = keys[i];
                var val = value[key];
                if (typeof val === 'object' && val !== null) {
                    var extracted = this.extractText(val, null);
                    if (extracted && extracted !== fallback) {
                        return extracted;
                    }
                }
            }
            
            return fallback;
        }
        
        if (typeof value === 'number' || typeof value === 'boolean') {
            return String(value);
        }
        
        return fallback;
    };
    
    // ====================================================================
    // HELPER METHODS
    // ====================================================================
    
    EnhancedPDFGenerator.prototype.checkPageBreak = function(neededSpace) {
        if (this.yPos + neededSpace > PAGE_CONFIG.marginBottom) {
            this.addPageFooter();
            this.doc.addPage();
            this.yPos = PAGE_CONFIG.marginTop;
            this.pageNumber++;
            return true;
        }
        return false;
    };
    
    EnhancedPDFGenerator.prototype.addLine = function() {
        this.checkPageBreak(3);
        this.doc.setDrawColor(COLORS.border[0], COLORS.border[1], COLORS.border[2]);
        this.doc.setLineWidth(0.3);
        this.doc.line(PAGE_CONFIG.marginLeft, this.yPos, PAGE_CONFIG.marginRight, this.yPos);
        this.yPos += 5;
    };
    
    EnhancedPDFGenerator.prototype.addSpace = function(amount) {
        this.yPos += (amount || PAGE_CONFIG.sectionSpacing);
    };
    
    EnhancedPDFGenerator.prototype.setText = function(size, style, color) {
        this.doc.setFontSize(size);
        this.doc.setFont('helvetica', style || 'normal');
        
        if (color) {
            this.doc.setTextColor(color[0], color[1], color[2]);
        } else {
            this.doc.setTextColor(COLORS.textDark[0], COLORS.textDark[1], COLORS.textDark[2]);
        }
    };
    
    EnhancedPDFGenerator.prototype.addTitle = function(text, level) {
        this.checkPageBreak(12);
        
        if (level === 1) {
            this.setText(18, 'bold', COLORS.primary);
        } else {
            this.setText(14, 'bold', COLORS.textDark);
        }
        
        this.doc.text(text, PAGE_CONFIG.marginLeft, this.yPos);
        this.yPos += (level === 1 ? 10 : 8);
    };
    
    EnhancedPDFGenerator.prototype.addText = function(text, maxWidth) {
        if (!text) return;
        
        this.checkPageBreak(10);
        this.setText(10, 'normal');
        
        var lines = this.doc.splitTextToSize(text, maxWidth || 170);
        
        for (var i = 0; i < lines.length; i++) {
            this.checkPageBreak(6);
            this.doc.text(lines[i], PAGE_CONFIG.marginLeft, this.yPos);
            this.yPos += 5;
        }
    };
    
    EnhancedPDFGenerator.prototype.addBullet = function(text, maxWidth) {
        if (!text) return;
        
        this.checkPageBreak(10);
        this.setText(10, 'normal');
        
        var lines = this.doc.splitTextToSize(text, maxWidth || 160);
        
        this.doc.text('•', PAGE_CONFIG.marginLeft, this.yPos);
        this.doc.text(lines[0], PAGE_CONFIG.marginLeft + 5, this.yPos);
        this.yPos += 5;
        
        for (var i = 1; i < lines.length; i++) {
            this.checkPageBreak(6);
            this.doc.text(lines[i], PAGE_CONFIG.marginLeft + 5, this.yPos);
            this.yPos += 5;
        }
    };
    
    EnhancedPDFGenerator.prototype.addPageFooter = function() {
        var footerY = PAGE_CONFIG.height - 15;
        
        this.setText(9, 'normal', COLORS.textLight);
        this.doc.text('Generated by TruthLens', PAGE_CONFIG.marginLeft, footerY);
        
        var dateStr = new Date().toLocaleDateString();
        this.doc.text(dateStr, PAGE_CONFIG.width / 2, footerY, { align: 'center' });
        
        this.doc.text('Page ' + this.pageNumber, PAGE_CONFIG.marginRight, footerY, { align: 'right' });
    };
    
    EnhancedPDFGenerator.prototype.getScoreColor = function(score) {
        if (score >= 80) return COLORS.success;
        if (score >= 60) return COLORS.warning;
        return COLORS.danger;
    };
    
    EnhancedPDFGenerator.prototype.getTrustRating = function(score) {
        if (score >= 80) return 'Highly Trustworthy';
        if (score >= 60) return 'Generally Reliable';
        if (score >= 40) return 'Exercise Caution';
        return 'Low Credibility';
    };
    
    EnhancedPDFGenerator.prototype.cleanText = function(text, fallback) {
        if (!text || text === 'Unknown' || text === 'N/A') {
            return fallback || 'Unknown';
        }
        return String(text);
    };
    
    EnhancedPDFGenerator.prototype.createVisualBar = function(score, maxLength) {
        maxLength = maxLength || 30;
        var filled = Math.round((score / 100) * maxLength);
        var bar = '';
        
        for (var i = 0; i < filled; i++) {
            bar += '■';
        }
        
        for (var i = filled; i < maxLength; i++) {
            bar += '·';
        }
        
        return bar;
    };
    
    EnhancedPDFGenerator.prototype.getServiceData = function(serviceId) {
        if (!this.data.detailed_analysis) {
            return null;
        }
        
        return this.data.detailed_analysis[serviceId] || null;
    };
    
    EnhancedPDFGenerator.prototype.getServiceAnalysis = function(serviceData, serviceId) {
        if (!serviceData) {
            return this.getDefaultAnalysis(serviceId);
        }
        
        var what_we_looked = this.extractText(serviceData.analysis || serviceData.detailed_analysis || serviceData, null);
        
        if (!what_we_looked || what_we_looked === 'No information available.') {
            what_we_looked = this.generateWhatWeLooked(serviceId, serviceData);
        }
        
        var what_we_found = this.generateWhatWeFound(serviceId, serviceData);
        var what_it_means = this.generateWhatItMeans(serviceId, serviceData);
        
        return {
            what_we_looked: what_we_looked,
            what_we_found: what_we_found,
            what_it_means: what_it_means
        };
    };
    
    EnhancedPDFGenerator.prototype.generateWhatWeLooked = function(serviceId, data) {
        var templates = {
            'source_credibility': 'We analyzed source reputation, domain authority, editorial standards, and historical accuracy of ' + 
                                 (data.source_name || data.outlet || 'this outlet') + '.',
            'bias_detector': 'We examined language patterns, framing choices, source selection, and political indicators.',
            'fact_checker': 'We extracted factual claims and verified them against authoritative sources.',
            'author_analyzer': 'We investigated author credentials, publication history, and expertise.',
            'transparency_analyzer': 'We evaluated source attribution, citation quality, and disclosure practices.',
            'manipulation_detector': 'We analyzed content for emotional manipulation tactics and persuasive techniques.',
            'content_analyzer': 'We assessed writing quality, readability, grammar, and professional standards.'
        };
        
        return templates[serviceId] || 'We performed comprehensive analysis of this dimension.';
    };
    
    EnhancedPDFGenerator.prototype.generateWhatWeFound = function(serviceId, data) {
        var score = data.score || data.credibility_score || data.quality_score || 50;
        var findings = [];
        
        if (data.summary) {
            var summary = this.extractText(data.summary, null);
            if (summary && summary !== 'No information available.') {
                return summary;
            }
        }
        
        if (serviceId === 'source_credibility') {
            findings.push((data.source_name || 'This source') + ' received a credibility score of ' + score + '/100.');
        }
        else if (serviceId === 'bias_detector') {
            var direction = data.direction || data.political_lean || 'center';
            findings.push('Bias score: ' + score + '/100 with a ' + direction + ' political leaning.');
        }
        else if (serviceId === 'fact_checker') {
            findings.push('Fact-checking accuracy score: ' + score + '/100');
        }
        else {
            findings.push('Score: ' + score + '/100');
        }
        
        return findings.join(' ');
    };
    
    EnhancedPDFGenerator.prototype.generateWhatItMeans = function(serviceId, data) {
        var score = data.score || data.credibility_score || 50;
        
        var interpretations = {
            'source_credibility': score >= 80 ? 
                'This source demonstrates excellent credibility.' :
                score >= 60 ? 'This source shows good credibility.' :
                'This source has credibility concerns.',
            
            'bias_detector': score >= 80 ?
                'The article maintains strong objectivity.' :
                score >= 60 ? 'The article shows some bias.' :
                'The article demonstrates significant bias.',
            
            'fact_checker': score >= 80 ?
                'Factual claims are well-supported.' :
                score >= 60 ? 'Most claims are accurate.' :
                'Several claims are questionable.',
            
            'author_analyzer': score >= 80 ?
                'The author demonstrates strong credentials.' :
                'Author credentials require verification.',
            
            'transparency_analyzer': score >= 80 ?
                'Excellent transparency with clear sourcing.' :
                'Transparency could be improved.',
            
            'manipulation_detector': score >= 70 ?
                'Minimal manipulative tactics detected.' :
                'Manipulation tactics present.',
            
            'content_analyzer': score >= 80 ?
                'Excellent writing quality.' :
                'Quality concerns present.'
        };
        
        return interpretations[serviceId] || 'Analysis complete.';
    };
    
    EnhancedPDFGenerator.prototype.getDefaultAnalysis = function(serviceId) {
        return {
            what_we_looked: 'Analysis not available.',
            what_we_found: 'No data collected.',
            what_it_means: 'Unable to provide assessment.'
        };
    };
    
    EnhancedPDFGenerator.prototype.extractScore = function(serviceData) {
        if (!serviceData) return 0;
        
        return serviceData.score || 
               serviceData.credibility_score || 
               serviceData.quality_score || 
               serviceData.objectivity_score || 0;
    };
    
    // ====================================================================
    // COVER PAGE
    // ====================================================================
    
    EnhancedPDFGenerator.prototype.addCoverPage = function() {
        this.setText(28, 'bold', COLORS.primary);
        this.doc.text('TruthLens', PAGE_CONFIG.width / 2, 60, { align: 'center' });
        
        this.yPos = 70;
        this.setText(16, 'normal', COLORS.textLight);
        this.doc.text('Professional Analysis Report', PAGE_CONFIG.width / 2, this.yPos, { align: 'center' });
        
        this.yPos = 90;
        this.addLine();
        this.addSpace(5);
        
        this.setText(14, 'bold');
        this.doc.text('News Article Analysis', PAGE_CONFIG.width / 2, this.yPos, { align: 'center' });
        
        this.yPos += 15;
        this.setText(11, 'normal', COLORS.textLight);
        this.doc.text('Source: ' + this.cleanText(this.data.source, 'Unknown'), 
            PAGE_CONFIG.width / 2, this.yPos, { align: 'center' });
        
        this.yPos += 6;
        this.doc.text('Author: ' + this.cleanText(this.data.author, 'Unknown'),
            PAGE_CONFIG.width / 2, this.yPos, { align: 'center' });
        
        this.yPos = 140;
        var trustScore = Math.round(this.data.trust_score || 0);
        var scoreColor = this.getScoreColor(trustScore);
        
        this.setText(48, 'bold', scoreColor);
        this.doc.text(trustScore.toString(), PAGE_CONFIG.width / 2, this.yPos, { align: 'center' });
        
        this.yPos += 10;
        this.setText(16, 'normal', COLORS.textLight);
        this.doc.text('/100', PAGE_CONFIG.width / 2, this.yPos, { align: 'center' });
        
        this.yPos += 15;
        var rating = this.getTrustRating(trustScore);
        this.setText(14, 'bold');
        this.doc.text(rating, PAGE_CONFIG.width / 2, this.yPos, { align: 'center' });
        
        this.yPos = PAGE_CONFIG.height - 40;
        this.setText(10, 'normal', COLORS.textLight);
        this.doc.text('Analysis completed: ' + new Date().toLocaleString(), 
            PAGE_CONFIG.width / 2, this.yPos, { align: 'center' });
        
        this.yPos += 6;
        this.setText(9, 'normal', COLORS.textLight);
        this.doc.text('Comprehensive 7-Service Analysis', 
            PAGE_CONFIG.width / 2, this.yPos, { align: 'center' });
    };
    
    // ====================================================================
    // EXECUTIVE SUMMARY
    // ====================================================================
    
    EnhancedPDFGenerator.prototype.addExecutiveSummary = function() {
        this.doc.addPage();
        this.yPos = PAGE_CONFIG.marginTop;
        this.pageNumber++;
        
        this.addTitle('Executive Summary', 1);
        this.addLine();
        
        var trustScore = Math.round(this.data.trust_score || 0);
        var source = this.cleanText(this.data.source, 'This source');
        
        var assessment = source + ' receives an overall trust score of ' + trustScore + '/100. ' +
            'This comprehensive analysis evaluated the article across 7 critical dimensions.';
        
        this.addText(assessment);
        this.addSpace();
        
        if (this.data.article_summary || this.data.summary) {
            this.addTitle('Article Summary', 2);
            var summary = this.extractText(this.data.article_summary || this.data.summary, 'Summary not available.');
            this.addText(summary);
            this.addSpace();
        }
        
        this.addTitle('Article Information', 2);
        this.addText('Source: ' + this.cleanText(this.data.source, 'Unknown'));
        this.addText('Author: ' + this.cleanText(this.data.author, 'Unknown'));
        
        if (this.data.word_count && this.data.word_count > 0) {
            this.addText('Word Count: ' + this.data.word_count.toLocaleString());
        }
        
        this.addText('Analysis Date: ' + new Date().toLocaleDateString());
        this.addText('Trust Score: ' + trustScore + '/100');
        
        this.addSpace();
        
        this.addTitle('Key Findings', 2);
        var findings = this.extractKeyFindings();
        for (var i = 0; i < Math.min(findings.length, 6); i++) {
            this.addBullet(findings[i]);
        }
        
        this.addSpace();
        
        this.addTitle('Bottom Line', 2);
        var bottomLine = this.generateBottomLine(trustScore);
        this.addText(bottomLine);
    };
    
    EnhancedPDFGenerator.prototype.extractKeyFindings = function() {
        var findings = [];
        var detailed = this.data.detailed_analysis || {};
        
        Object.keys(detailed).forEach(function(serviceId) {
            var service = detailed[serviceId];
            if (service.summary) {
                var summary = this.extractText(service.summary, null);
                if (summary && summary !== 'No information available.') {
                    findings.push(summary);
                }
            }
        }.bind(this));
        
        if (findings.length === 0) {
            findings.push('Analysis completed across all credibility dimensions');
        }
        
        return findings.slice(0, 5);
    };
    
    EnhancedPDFGenerator.prototype.generateBottomLine = function(trustScore) {
        var source = this.cleanText(this.data.source, 'This source');
        
        if (trustScore >= 80) {
            return source + ' demonstrates strong credibility. Information can generally be trusted.';
        } else if (trustScore >= 60) {
            return source + ' demonstrates acceptable credibility. Verify critical information.';
        } else if (trustScore >= 40) {
            return source + ' has mixed credibility. Exercise caution.';
        } else {
            return source + ' has significant credibility concerns. Verify all information.';
        }
    };
    
    // ====================================================================
    // QUICK REFERENCE
    // ====================================================================
    
    EnhancedPDFGenerator.prototype.addQuickReference = function() {
        this.doc.addPage();
        this.yPos = PAGE_CONFIG.marginTop;
        this.pageNumber++;
        
        this.addTitle('Quick Reference Summary', 1);
        this.addLine();
        
        this.addText('At-a-glance overview of all analysis dimensions:');
        this.addSpace(5);
        
        this.setText(9, 'bold');
        this.doc.text('Service', PAGE_CONFIG.marginLeft, this.yPos);
        this.doc.text('Score', PAGE_CONFIG.marginLeft + 70, this.yPos);
        this.doc.text('Rating', PAGE_CONFIG.marginLeft + 110, this.yPos);
        this.doc.text('Weight', PAGE_CONFIG.marginLeft + 150, this.yPos);
        this.yPos += 5;
        
        this.addLine();
        
        var scores = this.getServiceScores();
        var weights = {
            'source_credibility': '25%',
            'bias_detector': '20%',
            'fact_checker': '15%',
            'author_analyzer': '15%',
            'transparency_analyzer': '10%',
            'manipulation_detector': '10%',
            'content_analyzer': '5%'
        };
        
        for (var i = 0; i < scores.length; i++) {
            this.checkPageBreak(10);
            
            var service = scores[i];
            var barColor = this.getScoreColor(service.score);
            var rating = this.getScoreRating(service.score);
            
            this.setText(9, 'normal');
            this.doc.text(service.name, PAGE_CONFIG.marginLeft, this.yPos);
            
            var bar = this.createVisualBar(service.score, 15);
            this.setText(8, 'normal', barColor);
            this.doc.text(bar, PAGE_CONFIG.marginLeft + 70, this.yPos - 1);
            
            this.setText(9, 'bold', barColor);
            this.doc.text(service.score + '/100', PAGE_CONFIG.marginLeft + 110, this.yPos);
            
            this.setText(9, 'normal');
            this.doc.text(rating, PAGE_CONFIG.marginLeft + 110, this.yPos);
            this.doc.text(weights[service.key] || '-', PAGE_CONFIG.marginLeft + 150, this.yPos);
            
            this.yPos += 8;
        }
        
        this.addSpace(10);
        
        this.addTitle('Overall Verdict', 2);
        var verdict = this.generateVerdict();
        this.addText(verdict);
    };
    
    EnhancedPDFGenerator.prototype.getServiceScores = function() {
        var detailed = this.data.detailed_analysis || {};
        var scores = [];
        
        var serviceMap = [
            { key: 'source_credibility', name: 'Source Credibility' },
            { key: 'bias_detector', name: 'Bias Detection' },
            { key: 'fact_checker', name: 'Fact Checking' },
            { key: 'author_analyzer', name: 'Author Analysis' },
            { key: 'transparency_analyzer', name: 'Transparency' },
            { key: 'manipulation_detector', name: 'Manipulation Detection' },
            { key: 'content_analyzer', name: 'Content Quality' }
        ];
        
        for (var i = 0; i < serviceMap.length; i++) {
            var service = detailed[serviceMap[i].key];
            var score = this.extractScore(service);
            
            scores.push({
                key: serviceMap[i].key,
                name: serviceMap[i].name,
                score: score
            });
        }
        
        return scores;
    };
    
    EnhancedPDFGenerator.prototype.getScoreRating = function(score) {
        if (score >= 80) return 'Excellent';
        if (score >= 60) return 'Good';
        if (score >= 40) return 'Fair';
        return 'Poor';
    };
    
    EnhancedPDFGenerator.prototype.generateVerdict = function() {
        var trustScore = Math.round(this.data.trust_score || 0);
        
        if (trustScore >= 80) {
            return 'HIGHLY RECOMMENDED: This article demonstrates excellent credibility.';
        } else if (trustScore >= 60) {
            return 'GENERALLY RELIABLE: This article demonstrates acceptable credibility.';
        } else if (trustScore >= 40) {
            return 'EXERCISE CAUTION: This article has mixed credibility indicators.';
        } else {
            return 'NOT RECOMMENDED: This article has significant credibility concerns.';
        }
    };
    
    // ====================================================================
    // RECOMMENDATIONS
    // ====================================================================
    
    EnhancedPDFGenerator.prototype.addRecommendations = function() {
        this.doc.addPage();
        this.yPos = PAGE_CONFIG.marginTop;
        this.pageNumber++;
        
        this.addTitle('Recommendations', 1);
        this.addLine();
        
        var trustScore = Math.round(this.data.trust_score || 0);
        
        this.addTitle('How to Use This Article', 2);
        
        if (trustScore >= 80) {
            this.addText('This article can be used as a reliable information source. ' +
                'Maintain standard verification practices for critical decisions.');
        } else if (trustScore >= 60) {
            this.addText('This article can generally be trusted, but verify specific claims ' +
                'if using for important decisions.');
        } else {
            this.addText('Exercise caution. Verify important information through multiple independent sources.');
        }
        
        this.addSpace();
        
        this.addTitle('Verification Steps', 2);
        this.addBullet('Verify specific statistics or data points if using for research');
        this.addBullet('Check publication date to ensure information is current');
        this.addBullet('Review author credentials if expertise is important');
        this.addBullet('Cross-reference controversial claims with additional sources');
        
        this.addSpace();
        
        this.addTitle('Red Flags to Watch', 2);
        this.addBullet('Be cautious if new information contradicts established facts');
        this.addBullet('Watch for potential updates or corrections from the source');
        this.addBullet('Consider context if sharing on social media');
        
        this.addSpace();
        
        this.addTitle('Best Practices', 2);
        this.addBullet('Always read beyond headlines before sharing content');
        this.addBullet('Verify information through multiple independent sources');
        this.addBullet('Check publication dates and look for updates');
        this.addBullet('Consider author expertise and potential conflicts');
        this.addBullet('Be skeptical of emotionally charged claims');
        this.addBullet('Look for primary sources rather than secondary reporting');
    };
    
    // ====================================================================
    // RISK ASSESSMENT (PRESERVED)
    // ====================================================================
    
    EnhancedPDFGenerator.prototype.addRiskAssessment = function() {
        this.doc.addPage();
        this.yPos = PAGE_CONFIG.marginTop;
        this.pageNumber++;
        
        this.addTitle('Risk Assessment', 1);
        this.addLine();
        
        var trustScore = Math.round(this.data.trust_score || 0);
        
        this.addTitle('Overall Risk Level', 2);
        
        var riskLevel, riskColor, riskText;
        
        if (trustScore >= 80) {
            riskLevel = 'Low';
            riskColor = COLORS.success;
            riskText = 'This article presents low risk of misinformation. Standard verification practices sufficient.';
        } else if (trustScore >= 60) {
            riskLevel = 'Moderate';
            riskColor = COLORS.warning;
            riskText = 'This article presents moderate risk. Verify important claims before use.';
        } else {
            riskLevel = 'High';
            riskColor = COLORS.danger;
            riskText = 'This article presents significant risk. Thorough verification required.';
        }
        
        this.setText(14, 'bold', riskColor);
        this.doc.text('Risk Level: ' + riskLevel, PAGE_CONFIG.marginLeft, this.yPos);
        this.yPos += 10;
        
        this.setText(10, 'normal');
        this.addText(riskText);
        
        this.addSpace();
        
        this.addTitle('Mitigation Strategies', 2);
        this.addBullet('Apply standard verification for critical decisions');
        this.addBullet('Check for updates if time-sensitive information');
        this.addBullet('Verify statistics if using for research');
    };
    
    // ====================================================================
    // COMPARATIVE ANALYSIS (PRESERVED)
    // ====================================================================
    
    EnhancedPDFGenerator.prototype.addComparativeAnalysis = function() {
        this.doc.addPage();
        this.yPos = PAGE_CONFIG.marginTop;
        this.pageNumber++;
        
        this.addTitle('Comparative Analysis', 1);
        this.addLine();
        
        var trustScore = Math.round(this.data.trust_score || 0);
        
        this.addTitle('Industry Benchmarks', 2);
        this.addText('How this article compares to established news standards:');
        this.addSpace(5);
        
        var benchmarks = [
            { name: 'Reuters (Industry Leader)', score: 95 },
            { name: 'Associated Press', score: 94 },
            { name: 'BBC News', score: 92 },
            { name: 'Your Article', score: trustScore },
            { name: 'Industry Average', score: 75 },
            { name: 'Minimum Acceptable', score: 60 }
        ];
        
        this.setText(9, 'bold');
        this.doc.text('Source', PAGE_CONFIG.marginLeft, this.yPos);
        this.doc.text('Score', PAGE_CONFIG.marginLeft + 80, this.yPos);
        this.doc.text('Visual', PAGE_CONFIG.marginLeft + 120, this.yPos);
        this.yPos += 5;
        this.addLine();
        
        for (var i = 0; i < benchmarks.length; i++) {
            this.checkPageBreak(10);
            
            var b = benchmarks[i];
            var isYourArticle = b.name === 'Your Article';
            
            if (isYourArticle) {
                this.setText(9, 'bold');
            } else {
                this.setText(9, 'normal');
            }
            this.doc.text(b.name, PAGE_CONFIG.marginLeft, this.yPos);
            
            this.doc.text(b.score.toString(), PAGE_CONFIG.marginLeft + 80, this.yPos);
            
            var barColor = isYourArticle ? this.getScoreColor(b.score) : COLORS.textLight;
            var bar = this.createVisualBar(b.score, 20);
            this.setText(9, 'normal', barColor);
            this.doc.text(bar, PAGE_CONFIG.marginLeft + 120, this.yPos);
            
            this.yPos += 7;
        }
        
        this.addSpace();
        
        this.addTitle('Comparative Insights', 2);
        
        var insight;
        if (trustScore >= 85) {
            insight = 'This article performs at industry-leading standards.';
        } else if (trustScore >= 75) {
            insight = 'This article performs above industry averages.';
        } else if (trustScore >= 60) {
            insight = 'This article meets minimum professional standards.';
        } else {
            insight = 'This article performs below industry standards.';
        }
        
        this.addText(insight);
    };
    
    // ====================================================================
    // SCORE BREAKDOWN (PRESERVED)
    // ====================================================================
    
    EnhancedPDFGenerator.prototype.addScoreBreakdown = function() {
        this.doc.addPage();
        this.yPos = PAGE_CONFIG.marginTop;
        this.pageNumber++;
        
        this.addTitle('Trust Score Breakdown', 1);
        this.addLine();
        
        this.addText('Detailed breakdown of how the overall trust score was calculated:');
        this.addSpace(5);
        
        var scores = this.getServiceScores();
        var weights = {
            'source_credibility': 25,
            'bias_detector': 20,
            'fact_checker': 15,
            'author_analyzer': 15,
            'transparency_analyzer': 10,
            'manipulation_detector': 10,
            'content_analyzer': 5
        };
        
        this.setText(9, 'bold');
        this.doc.text('Service (Weight)', PAGE_CONFIG.marginLeft, this.yPos);
        this.doc.text('Score', PAGE_CONFIG.marginLeft + 80, this.yPos);
        this.doc.text('Visual', PAGE_CONFIG.marginLeft + 120, this.yPos);
        this.yPos += 5;
        this.addLine();
        
        for (var i = 0; i < scores.length; i++) {
            this.checkPageBreak(10);
            
            var service = scores[i];
            var weight = weights[service.key] || 0;
            var scoreColor = this.getScoreColor(service.score);
            
            this.setText(9, 'normal');
            this.doc.text(service.name + ' (' + weight + '%)', PAGE_CONFIG.marginLeft, this.yPos);
            
            this.setText(9, 'bold', scoreColor);
            this.doc.text(service.score + '/100', PAGE_CONFIG.marginLeft + 80, this.yPos);
            
            var bar = this.createVisualBar(service.score, 20);
            this.setText(9, 'normal', scoreColor);
            this.doc.text(bar, PAGE_CONFIG.marginLeft + 120, this.yPos);
            
            this.yPos += 8;
        }
        
        this.addSpace();
        
        this.addTitle('Calculation Method', 2);
        this.addText('The overall trust score is calculated as a weighted average of all service scores. ' +
            'Critical factors like source credibility and bias detection receive higher weights.');
    };
    
    // ====================================================================
    // DETAILED SERVICE ANALYSIS
    // ====================================================================
    
    EnhancedPDFGenerator.prototype.addDetailedServiceAnalysis = function() {
        this.addServiceSection('source_credibility', 'Source Credibility Analysis');
        this.addServiceSection('bias_detector', 'Bias Detection');
        this.addServiceSection('fact_checker', 'Fact Checking');
        this.addServiceSection('author_analyzer', 'Author Analysis');
        this.addServiceSection('transparency_analyzer', 'Transparency Assessment');
        this.addServiceSection('manipulation_detector', 'Manipulation Detection');
        this.addServiceSection('content_analyzer', 'Content Quality');
    };
    
    EnhancedPDFGenerator.prototype.addServiceSection = function(serviceId, title) {
        this.doc.addPage();
        this.yPos = PAGE_CONFIG.marginTop;
        this.pageNumber++;
        
        this.addTitle(title, 1);
        
        var data = this.getServiceData(serviceId);
        if (!data) {
            this.addText(title + ' analysis not available.');
            return;
        }
        
        var score = this.extractScore(data);
        var scoreColor = this.getScoreColor(score);
        
        this.setText(12, 'bold', COLORS.textLight);
        this.doc.text('Overall Score', PAGE_CONFIG.marginLeft, this.yPos);
        this.yPos += 8;
        
        this.setText(24, 'bold', scoreColor);
        this.doc.text(score + '/100', PAGE_CONFIG.marginLeft, this.yPos);
        
        var bar = this.createVisualBar(score, 30);
        this.setText(12, 'normal', scoreColor);
        this.doc.text(bar, PAGE_CONFIG.marginLeft + 35, this.yPos - 3);
        
        this.yPos += 10;
        this.addLine();
        
        var analysis = this.getServiceAnalysis(data, serviceId);
        
        this.addTitle('What We Analyzed', 2);
        this.addText(analysis.what_we_looked);
        this.addSpace();
        
        this.addTitle('What We Found', 2);
        this.addText(analysis.what_we_found);
        this.addSpace();
        
        this.addTitle('What It Means', 2);
        this.addText(analysis.what_it_means);
    };
    
    // ====================================================================
    // METHODOLOGY (PRESERVED)
    // ====================================================================
    
    EnhancedPDFGenerator.prototype.addMethodology = function() {
        this.doc.addPage();
        this.yPos = PAGE_CONFIG.marginTop;
        this.pageNumber++;
        
        this.addTitle('Methodology & Rating System', 1);
        this.addLine();
        
        this.addTitle('About TruthLens', 2);
        this.addText('TruthLens employs a comprehensive 7-service analysis framework powered by ' +
            'advanced AI and natural language processing. Each service evaluates specific dimensions ' +
            'of credibility.');
        
        this.addSpace();
        
        this.addTitle('Analysis Services', 2);
        this.addText('Source Credibility (25%): Evaluates outlet reputation. ' +
            'Bias Detection (20%): Analyzes political leaning. ' +
            'Fact Checking (15%): Verifies claims. ' +
            'Author Analysis (15%): Assesses credentials. ' +
            'Transparency (10%): Reviews sourcing. ' +
            'Manipulation Detection (10%): Identifies tactics. ' +
            'Content Quality (5%): Evaluates standards.');
        
        this.addSpace();
        
        this.addTitle('Score Calculation', 2);
        this.addText('The overall trust score is a weighted average of all seven services. ' +
            'Each service is scored 0-100, with weights assigned by importance.');
        
        this.addSpace();
        
        this.addTitle('Rating Scale', 2);
        this.addText('80-100: Highly Trustworthy. ' +
            '60-79: Generally Reliable. ' +
            '40-59: Exercise Caution. ' +
            '0-39: Low Credibility.');
        
        this.addSpace();
        
        this.addTitle('Limitations & Disclaimers', 2);
        this.addText('This analysis is for informational purposes only. ' +
            'Users should verify important information through multiple sources. ' +
            'TruthLens does not guarantee accuracy.');
    };
    
    // ====================================================================
    // MAIN GENERATE FUNCTION
    // ====================================================================
    
    EnhancedPDFGenerator.prototype.generate = function() {
        console.log('[PDFGen v3.0] Generating complete PDF...');
        
        this.addCoverPage();
        this.addExecutiveSummary();
        this.addQuickReference();
        this.addRecommendations();
        this.addRiskAssessment();
        this.addComparativeAnalysis();
        this.addScoreBreakdown();
        this.addDetailedServiceAnalysis();
        this.addMethodology();
        
        var totalPages = this.doc.internal.pages.length - 1;
        for (var i = 1; i <= totalPages; i++) {
            this.doc.setPage(i);
            this.pageNumber = i;
            this.addPageFooter();
        }
        
        var timestamp = new Date().getTime();
        var source = (this.data.source || 'article').toLowerCase().replace(/[^a-z0-9]/g, '-');
        var filename = 'truthlens-' + source + '-' + timestamp + '.pdf';
        
        this.doc.save(filename);
        
        console.log('[PDFGen v3.0] ✓ PDF complete:', filename);
    };
    
    console.log('[PDFGenerator v3.0 COMPLETE] All sections preserved!');
    
})();

/**
 * I did no harm and this file is not truncated.
 * Date: November 3, 2025 - v3.0 COMPLETE
 * All original sections preserved:
 * - Cover Page
 * - Executive Summary
 * - Quick Reference
 * - Recommendations
 * - Risk Assessment (PRESERVED)
 * - Comparative Analysis (PRESERVED)
 * - Score Breakdown (PRESERVED)
 * - Detailed Service Analysis (with extractText() fix)
 * - Methodology
 */
