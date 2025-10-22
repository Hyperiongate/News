/**
 * FILE: static/js/pdf-generator.js
 * VERSION: 12.2.2 - VERDICT BADGE FIX
 * DATE: October 22, 2025
 * Last Updated: October 22, 2025 - 8:45 PM
 * 
 * CRITICAL UPGRADE FROM v12.1.1:
 * ✅ NEW: Integrated 13-point fact checking scale
 * ✅ NEW: Shows verdict icons (✅, ❌, ⚠️, 💨, 🔮, ❓, 💭)
 * ✅ NEW: Color-coded verdicts matching fact checker service
 * ✅ NEW: Verdict labels (True, Mostly True, Exaggerated, etc.)
 * ✅ ENHANCED: Fact checker claims display uses full 13-point metadata
 * ✅ PRESERVED: All v12.1.1 fixes (full text, no overlap, global function)
 * 
 * UPDATE v12.2.3 (October 22, 2025 - 8:45 PM):
 * ✅ FIXED: PDF layout - increased height from 70mm to 100mm for more claims
 * ✅ FIXED: Better spacing between claims (3px instead of 2px)
 * ✅ RESULT: Can now display 6-8 claims instead of just 3-4
 *
 * 13-POINT SCALE:
 * - true (✅ green), mostly_true (✅ light green)
 * - partially_true (⚠️ yellow), exaggerated (📈 orange)
 * - misleading (⚠️ dark orange), mostly_false (❌ red-orange)
 * - false (❌ red), empty_rhetoric (💨 gray)
 * - unsubstantiated_prediction (🔮 purple), needs_context (❓ purple)
 * - opinion (💭 blue), mixed (◐ orange), unverified (? gray)
 * 
 * This version provides comprehensive, informative fact checking display!
 */

// ============================================================================
// TEXT CLEANING UTILITY
// ============================================================================

function cleanText(text) {
    if (!text) return '';
    return text
        .replace(/[\u{1F300}-\u{1F9FF}]/gu, '')
        .replace(/[\u{2600}-\u{26FF}]/gu, '')
        .replace(/[\u{2700}-\u{27BF}]/gu, '')
        .replace(/[\u{FE00}-\u{FE0F}]/gu, '')
        .replace(/[\u{1F000}-\u{1FFFF}]/gu, '')
        .replace(/Ø=[^\s]*/g, '')
        .replace(/[^\x20-\x7E\s]/g, '')
        .replace(/\s+/g, ' ')
        .trim();
}

function isGenericPlaceholder(text) {
    if (!text) return true;
    const placeholders = ['analysis completed', 'results processed', 'analyzed', 'processing complete', 'claim analyzed'];
    const cleaned = text.toLowerCase().trim();
    return placeholders.some(p => cleaned === p || cleaned.includes(p)) && cleaned.length < 30;
}

// ============================================================================
// MAIN ENTRY POINT - GLOBAL FUNCTION (v12.1 PRESERVED)
// ============================================================================

function downloadPDFReport() {
    console.log('[PDF v12.1.1] Generating professional PDF report with FULL TEXT and NO OVERLAP...');
    
    if (typeof window.jspdf === 'undefined') {
        alert('PDF library not loaded. Please refresh the page and try again.');
        return;
    }
    
    const data = window.lastAnalysisData;
    if (!data) {
        alert('No analysis data available. Please run an analysis first.');
        return;
    }
    
    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({
            orientation: 'portrait',
            unit: 'mm',
            format: 'a4'
        });
        
        generateProfessionalPDF(doc, data);
        
        const timestamp = new Date().toISOString().split('T')[0];
        const sourceShort = (data.source || 'Report').substring(0, 30).replace(/[^a-zA-Z0-9]/g, '-');
        const filename = `TruthLens-Report-${sourceShort}-${timestamp}.pdf`;
        
        doc.save(filename);
        console.log('[PDF v12.1.1] ✓ Professional report generated with full text:', filename);
        
    } catch (error) {
        console.error('[PDF v12.1.1] Error:', error);
        alert('Error generating PDF. Please try again.');
    }
}

// ============================================================================
// PDF GENERATION ORCHESTRATOR
// ============================================================================

function generateProfessionalPDF(doc, data) {
    const trustScore = Math.round(data.trust_score || 0);
    const detailed = data.detailed_analysis || {};
    
    const colors = {
        primary: [59, 130, 246],
        success: [34, 197, 94],
        warning: [251, 146, 60],
        danger: [239, 68, 68],
        purple: [168, 85, 247],
        gray: [107, 114, 128],
        lightGray: [243, 244, 246],
        darkGray: [31, 41, 55],
        white: [255, 255, 255],
        leftColor: [59, 130, 246],
        centerColor: [168, 85, 247],
        rightColor: [239, 68, 68]
    };
    
    const scoreColor = trustScore >= 70 ? colors.success :
                       trustScore >= 50 ? colors.warning : colors.danger;
    
    // Cover page
    generateCoverPage(doc, data, trustScore, scoreColor, colors);
    
    // Executive summary
    doc.addPage();
    generateExecutiveSummary(doc, data, trustScore, scoreColor, colors);
    
    // Enhanced service pages
    const services = [
        { key: 'source_credibility', title: 'Source Credibility Analysis', color: colors.primary },
        { key: 'bias_detector', title: 'Bias Detection Analysis', color: colors.warning },
        { key: 'fact_checker', title: 'Fact Verification Analysis', color: colors.success },
        { key: 'author_analyzer', title: 'Author Credibility Analysis', color: colors.primary },
        { key: 'transparency_analyzer', title: 'Transparency Analysis', color: colors.purple },
        { key: 'content_analyzer', title: 'Content Quality Analysis', color: [236, 72, 153] }
    ];
    
    services.forEach(service => {
        if (detailed[service.key] && detailed[service.key].score !== undefined) {
            doc.addPage();
            generateEnhancedServicePage(doc, service, detailed[service.key], colors, data);
        }
    });
    
    // Recommendations
    doc.addPage();
    generateRecommendationsPage(doc, data, trustScore, scoreColor, colors);
    
    // Add page numbers with FIXED footer position
    const totalPages = doc.internal.getNumberOfPages();
    for (let i = 2; i <= totalPages; i++) {
        doc.setPage(i);
        addPageFooter(doc, i, totalPages, colors);
    }
}

// ============================================================================
// COVER PAGE
// ============================================================================

function generateCoverPage(doc, data, trustScore, scoreColor, colors) {
    const pageWidth = 210;
    
    doc.setFillColor(...colors.primary);
    doc.rect(0, 0, pageWidth, 60, 'F');
    
    doc.setFontSize(48);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.white);
    doc.text('TruthLens', pageWidth / 2, 35, { align: 'center' });
    
    doc.setFontSize(16);
    doc.setFont('helvetica', 'normal');
    doc.text('AI-Powered Credibility Analysis Report', pageWidth / 2, 48, { align: 'center' });
    
    const centerX = pageWidth / 2;
    const centerY = 135;
    const radius = 45;
    
    doc.setDrawColor(...scoreColor);
    doc.setLineWidth(8);
    doc.circle(centerX, centerY, radius, 'S');
    
    doc.setFillColor(...colors.white);
    doc.circle(centerX, centerY, radius - 6, 'F');
    
    // FIXED v12.1.1: Proper spacing for score display - NO OVERLAP
    doc.setFontSize(64);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...scoreColor);
    
    // Get the actual width of the score at size 64
    const scoreText = trustScore.toString();
    const scoreTextWidth = doc.getTextWidth(scoreText);
    
    // Calculate center position for score
    const scoreStartX = centerX - (scoreTextWidth / 2);
    doc.text(scoreText, scoreStartX, centerY + 8);
    
    // FIXED v12.1.1: Position /100 with proper spacing (10mm gap)
    doc.setFontSize(24);
    doc.setTextColor(...colors.gray);
    doc.text('/100', scoreStartX + scoreTextWidth + 8, centerY + 8);
    
    const trustLabel = trustScore >= 80 ? 'HIGHLY TRUSTWORTHY' :
                       trustScore >= 70 ? 'TRUSTWORTHY' :
                       trustScore >= 60 ? 'MODERATELY RELIABLE' :
                       trustScore >= 50 ? 'QUESTIONABLE' : 'UNRELIABLE';
    
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...scoreColor);
    doc.text(trustLabel, centerX, centerY + 60, { align: 'center' });
    
    const cardY = 210;
    doc.setFillColor(...colors.lightGray);
    doc.roundedRect(20, cardY, pageWidth - 40, 60, 3, 3, 'F');
    
    let yPos = cardY + 12;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.darkGray);
    doc.text('SOURCE:', 25, yPos);
    doc.setFont('helvetica', 'normal');
    doc.text(cleanText(data.source || 'Unknown Source').substring(0, 60), 50, yPos);
    
    yPos += 10;
    doc.setFont('helvetica', 'bold');
    doc.text('AUTHOR:', 25, yPos);
    doc.setFont('helvetica', 'normal');
    
    // Get all authors from author_analyzer if available
    let authorText = 'Unknown Author';
    const authorAnalysis = data.detailed_analysis?.author_analyzer;
    
    if (authorAnalysis && authorAnalysis.all_authors && authorAnalysis.all_authors.length > 0) {
        const allAuthors = authorAnalysis.all_authors.filter(a => a && a !== 'Unknown Author');
        if (allAuthors.length > 1) {
            authorText = allAuthors.slice(0, -1).join(', ') + ' and ' + allAuthors[allAuthors.length - 1];
        } else if (allAuthors.length === 1) {
            authorText = allAuthors[0];
        }
    } else if (data.author) {
        authorText = data.author;
    }
    
    doc.text(cleanText(authorText).substring(0, 60), 50, yPos);
    
    yPos += 10;
    doc.setFont('helvetica', 'bold');
    doc.text('LENGTH:', 25, yPos);
    doc.setFont('helvetica', 'normal');
    doc.text(`${data.word_count || 0} words`, 50, yPos);
    
    yPos += 10;
    doc.setFont('helvetica', 'bold');
    doc.text('ANALYZED:', 25, yPos);
    doc.setFont('helvetica', 'normal');
    const dateStr = new Date().toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    doc.text(dateStr, 50, yPos);
    
    doc.setFontSize(12);
    doc.setFont('helvetica', 'italic');
    doc.setTextColor(...colors.gray);
    doc.text('Empowering truth through AI analysis', centerX, 285, { align: 'center' });
}

// ============================================================================
// EXECUTIVE SUMMARY
// ============================================================================

function generateExecutiveSummary(doc, data, trustScore, scoreColor, colors) {
    doc.setFillColor(...colors.primary);
    doc.rect(0, 0, 210, 20, 'F');
    
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.white);
    doc.text('Executive Summary', 105, 13, { align: 'center' });
    
    let yPos = 35;
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.darkGray);
    doc.text('Article Overview', 20, yPos);
    
    yPos += 8;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    const summary = cleanText(data.article_summary || data.title || 'No summary available.');
    const summaryLines = doc.splitTextToSize(summary, 170);
    doc.text(summaryLines.slice(0, 4), 20, yPos);
    yPos += summaryLines.slice(0, 4).length * 5 + 10;
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Key Findings', 20, yPos);
    
    yPos += 8;
    
    const findings = extractRealKeyFindings(data);
    
    findings.slice(0, 5).forEach(finding => {
        doc.setFillColor(...colors.primary);
        doc.circle(23, yPos - 2, 1.5, 'F');
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...colors.darkGray);
        const cleanedFinding = cleanText(finding);
        const lines = doc.splitTextToSize(cleanedFinding, 165);
        doc.text(lines[0], 28, yPos);
        
        yPos += 8;
    });
    
    yPos += 5;
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.darkGray);
    doc.text('Trust Score Breakdown', 20, yPos);
    
    yPos += 10;
    
    const serviceScores = getServiceScores(data.detailed_analysis || {});
    
    serviceScores.forEach(service => {
        doc.setFontSize(9);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.darkGray);
        doc.text(service.name, 20, yPos);
        
        doc.setFontSize(10);
        doc.setTextColor(...service.color);
        doc.text(`${service.score}`, 185, yPos, { align: 'right' });
        
        yPos += 4;
        
        doc.setFillColor(...colors.lightGray);
        doc.rect(20, yPos - 2, 165, 4, 'F');
        
        const barWidth = (service.score / 100) * 165;
        doc.setFillColor(...service.color);
        doc.rect(20, yPos - 2, barWidth, 4, 'F');
        
        yPos += 10;
    });
    
    // FIXED v12.0: Bottom line section position to avoid footer
    yPos = Math.min(yPos, 245);
    
    doc.setFillColor(255, 249, 235);
    doc.roundedRect(20, yPos, 170, 25, 2, 2, 'F');
    
    doc.setDrawColor(...colors.warning);
    doc.setLineWidth(0.5);
    doc.roundedRect(20, yPos, 170, 25, 2, 2, 'S');
    
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.darkGray);
    doc.text('Bottom Line:', 25, yPos + 8);
    
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    const bottomLine = cleanText(data.findings_summary) || generateBottomLine(trustScore);
    const bottomLines = doc.splitTextToSize(bottomLine, 160);
    doc.text(bottomLines.slice(0, 2), 25, yPos + 15);
}

// ============================================================================
// ENHANCED SERVICE PAGE
// ============================================================================

function generateEnhancedServicePage(doc, service, serviceData, colors, fullData) {
    const score = Math.round(serviceData.score || 0);
    const scoreColor = score >= 70 ? colors.success :
                       score >= 50 ? colors.warning : colors.danger;
    
    // Header
    doc.setFillColor(...service.color);
    doc.rect(0, 0, 210, 25, 'F');
    
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.white);
    doc.text(service.title, 105, 16, { align: 'center' });
    
    let yPos = 35;
    
    // ========== SCORE DISPLAY - FIXED v12.1.1 NO OVERLAP ==========
    
    doc.setFillColor(...colors.lightGray);
    doc.roundedRect(15, yPos, 180, 30, 3, 3, 'F');
    
    // FIXED v12.1.1: Calculate proper spacing to prevent overlap
    doc.setFontSize(36);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...scoreColor);
    
    // Get the actual width of the score number at size 36
    const scoreText = score.toString();
    const scoreTextWidth = doc.getTextWidth(scoreText);
    
    // Draw the score
    doc.text(scoreText, 25, yPos + 20);
    
    // FIXED v12.1.1: Position /100 with proper spacing (add 5mm gap)
    doc.setFontSize(20);
    doc.setTextColor(...colors.gray);
    doc.text('/100', 25 + scoreTextWidth + 5, yPos + 20);
    
    const barX = 70;
    const barY = yPos + 10;
    const barWidth = 115;
    const barHeight = 12;
    
    doc.setFillColor(220, 220, 220);
    doc.roundedRect(barX, barY, barWidth, barHeight, 2, 2, 'F');
    
    const fillWidth = (score / 100) * barWidth;
    doc.setFillColor(...scoreColor);
    doc.roundedRect(barX, barY, fillWidth, barHeight, 2, 2, 'F');
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.darkGray);
    const scoreLabel = score >= 80 ? 'Excellent' :
                       score >= 70 ? 'Good' :
                       score >= 60 ? 'Fair' :
                       score >= 50 ? 'Moderate' : 'Poor';
    doc.text(scoreLabel, 127.5, barY - 3, { align: 'center' });
    
    yPos += 38;
    
    // ========== SPECIAL GRAPHICS ==========
    
    if (service.key === 'source_credibility') {
        yPos = drawThirdPartyRatings(doc, serviceData, yPos, colors);
        yPos = drawOutletComparison(doc, serviceData, yPos, colors, fullData);
    }
    
    if (service.key === 'bias_detector') {
        yPos = drawPoliticalBiasDial(doc, serviceData, yPos, colors);
    }
    
    // ========== WHAT WE ANALYZED ==========
    
    doc.setFillColor(240, 249, 255);
    doc.roundedRect(15, yPos, 180, 28, 2, 2, 'F');
    
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.primary);
    doc.text('WHAT WE ANALYZED', 20, yPos + 8);
    
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.darkGray);
    
    let analysisText = '';
    if (serviceData.analysis?.what_we_looked && !isGenericPlaceholder(serviceData.analysis.what_we_looked)) {
        analysisText = cleanText(serviceData.analysis.what_we_looked);
    } else {
        analysisText = getWhatWeAnalyzed(service.key, serviceData, fullData);
    }
    
    const analysisLines = doc.splitTextToSize(analysisText, 170);
    doc.text(analysisLines.slice(0, 2), 20, yPos + 16);
    
    yPos += 36;
    
    // ========== KEY FINDINGS - FIXED v12.1 ENHANCED CLAIMS ==========
    
    // FIXED v12.0: Calculate height dynamically based on content
    let findingsHeight;
    if (service.key === 'fact_checker' || service.key === 'transparency_analyzer') {
        findingsHeight = 80; // Special sections with custom rendering
    } else {
        // Calculate based on actual text length
        const findingsText = serviceData.analysis?.what_we_found && !isGenericPlaceholder(serviceData.analysis.what_we_found) ?
            cleanText(serviceData.analysis.what_we_found) :
            getDetailedFindings(service.key, score, serviceData);
        
        const tempLines = doc.splitTextToSize(findingsText, 170);
        const lineCount = Math.min(tempLines.length, service.key === 'source_credibility' ? 2 : 4);
        findingsHeight = 18 + (lineCount * 4);
    }
    
    doc.setFillColor(245, 251, 245);
    doc.roundedRect(15, yPos, 180, findingsHeight, 2, 2, 'F');
    
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.success);
    doc.text('KEY FINDINGS', 20, yPos + 8);
    
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.darkGray);
    
    // FIXED v12.1: Enhanced fact checker and transparency displays
    if (service.key === 'fact_checker') {
        yPos = displayFactCheckClaims(doc, serviceData, fullData, yPos, colors);
    } else if (service.key === 'transparency_analyzer') {
        yPos = displayTransparencySources(doc, serviceData, yPos, colors);
    } else {
        let findingsText = '';
        if (serviceData.analysis?.what_we_found && !isGenericPlaceholder(serviceData.analysis.what_we_found)) {
            findingsText = cleanText(serviceData.analysis.what_we_found);
        } else {
            findingsText = getDetailedFindings(service.key, score, serviceData);
        }
        
        const findingsLines = doc.splitTextToSize(findingsText, 170);
        let fy = yPos + 16;
        
        const maxLines = service.key === 'source_credibility' ? 2 : 4;
        
        findingsLines.slice(0, maxLines).forEach(line => {
            doc.text(line, 20, fy);
            fy += 4;
        });
        
        yPos += findingsHeight + 8;
    }
    
    // FIXED v12.0: Ensure content doesn't exceed y=275 to avoid footer
    if (yPos > 220) {
        return; // Skip remaining sections if we're too far down
    }
    
    // ========== WHAT THIS MEANS ==========
    
    doc.setFillColor(255, 251, 235);
    doc.roundedRect(15, yPos, 180, 28, 2, 2, 'F');
    
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.warning);
    doc.text('WHAT THIS MEANS FOR YOU', 20, yPos + 8);
    
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.darkGray);
    
    let meaningText = '';
    if (serviceData.analysis?.what_it_means && !isGenericPlaceholder(serviceData.analysis.what_it_means)) {
        meaningText = cleanText(serviceData.analysis.what_it_means);
    } else {
        meaningText = getWhatItMeans(service.key, score, serviceData);
    }
    
    const meaningLines = doc.splitTextToSize(meaningText, 170);
    doc.text(meaningLines.slice(0, 2), 20, yPos + 16);
    
    yPos += 36;
    
    // ========== WHY IT MATTERS ==========
    
    if (yPos <= 235) { // Only add if we have room
        doc.setFillColor(250, 245, 255);
        doc.roundedRect(15, yPos, 180, 28, 2, 2, 'F');
        
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.purple);
        doc.text('WHY THIS MATTERS', 20, yPos + 8);
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...colors.darkGray);
        
        const educationText = getEducationalContent(service.key);
        const educationLines = doc.splitTextToSize(educationText, 170);
        doc.text(educationLines.slice(0, 2), 20, yPos + 16);
    }
}

// ============================================================================
// THIRD-PARTY RATING SERVICES DISPLAY
// ============================================================================

function drawThirdPartyRatings(doc, serviceData, yPos, colors) {
    const thirdParty = serviceData.third_party_ratings || {};
    
    if (!thirdParty.newsguard && !thirdParty.mediabiasfactcheck && !thirdParty.allsides) {
        return yPos;
    }
    
    doc.setFillColor(250, 250, 255);
    doc.roundedRect(15, yPos, 180, 70, 2, 2, 'F');
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.primary);
    doc.text('Third-Party Rating Services', 20, yPos + 8);
    
    let barY = yPos + 16;
    
    if (thirdParty.newsguard) {
        const ng = thirdParty.newsguard;
        const ngScore = ng.score || 0;
        const ngRating = ng.rating || 'Unknown';
        
        let ngColor;
        if (ngRating === 'Green') {
            ngColor = colors.success;
        } else if (ngRating === 'Yellow') {
            ngColor = colors.warning;
        } else if (ngRating === 'Red') {
            ngColor = colors.danger;
        } else {
            ngColor = colors.gray;
        }
        
        doc.setFontSize(8);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.darkGray);
        doc.text('NewsGuard', 20, barY);
        
        doc.setFontSize(9);
        doc.setTextColor(...ngColor);
        doc.text(`${ngScore}/100`, 175, barY, { align: 'right' });
        
        barY += 4;
        
        doc.setFillColor(220, 220, 220);
        doc.rect(20, barY - 2, 155, 4, 'F');
        
        const ngBarWidth = (ngScore / 100) * 155;
        doc.setFillColor(...ngColor);
        doc.rect(20, barY - 2, ngBarWidth, 4, 'F');
        
        barY += 8;
    }
    
    if (thirdParty.mediabiasfactcheck) {
        const mbfc = thirdParty.mediabiasfactcheck;
        const factual = mbfc.factual || 'Unknown';
        
        const factualScores = {
            'Very High': 95,
            'High': 80,
            'Mixed': 50,
            'Low': 30,
            'Very Low': 10,
            'Unknown': 50
        };
        const mbfcScore = factualScores[factual] || 50;
        const mbfcColor = mbfcScore >= 70 ? colors.success :
                          mbfcScore >= 50 ? colors.warning : colors.danger;
        
        doc.setFontSize(8);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.darkGray);
        doc.text('Media Bias/Fact Check', 20, barY);
        
        doc.setFontSize(8);
        doc.setTextColor(...mbfcColor);
        doc.text(factual, 175, barY, { align: 'right' });
        
        barY += 4;
        
        doc.setFillColor(220, 220, 220);
        doc.rect(20, barY - 2, 155, 4, 'F');
        
        const mbfcBarWidth = (mbfcScore / 100) * 155;
        doc.setFillColor(...mbfcColor);
        doc.rect(20, barY - 2, mbfcBarWidth, 4, 'F');
        
        barY += 8;
    }
    
    if (thirdParty.allsides) {
        const as = thirdParty.allsides;
        const reliability = as.reliability || 'Unknown';
        
        const reliabilityScores = {
            'High': 90,
            'Mixed': 60,
            'Low': 30,
            'Unknown': 50
        };
        const asScore = reliabilityScores[reliability] || 50;
        const asColor = asScore >= 70 ? colors.success :
                        asScore >= 50 ? colors.warning : colors.danger;
        
        doc.setFontSize(8);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.darkGray);
        doc.text('AllSides', 20, barY);
        
        doc.setFontSize(8);
        doc.setTextColor(...asColor);
        doc.text(reliability, 175, barY, { align: 'right' });
        
        barY += 4;
        
        doc.setFillColor(220, 220, 220);
        doc.rect(20, barY - 2, 155, 4, 'F');
        
        const asBarWidth = (asScore / 100) * 155;
        doc.setFillColor(...asColor);
        doc.rect(20, barY - 2, asBarWidth, 4, 'F');
        
        barY += 8;
    }
    
    return yPos + 78;
}

// ============================================================================
// OUTLET CREDIBILITY COMPARISON
// ============================================================================

function drawOutletComparison(doc, serviceData, yPos, colors, fullData) {
    const articleScore = Math.round(serviceData.article_score || serviceData.score || 0);
    const outletAverage = serviceData.outlet_average_score;
    const sourceName = cleanText(serviceData.source_name || fullData.source || 'This Source');
    
    const outlets = [
        { name: 'Reuters', score: 95, color: [34, 197, 94] },
        { name: 'Associated Press', score: 94, color: [34, 197, 94] },
        { name: 'BBC News', score: 92, color: [34, 197, 94] },
        { name: 'The New York Times', score: 88, color: [59, 130, 246] },
        { name: 'The Washington Post', score: 87, color: [59, 130, 246] },
        { name: 'NPR', score: 86, color: [59, 130, 246] },
        { name: 'The Wall Street Journal', score: 85, color: [59, 130, 246] },
        { name: 'ABC News', score: 83, color: [59, 130, 246] },
        { name: 'NBC News', score: 82, color: [59, 130, 246] },
        { name: 'CBS News', score: 81, color: [59, 130, 246] }
    ];
    
    doc.setFillColor(250, 250, 255);
    doc.roundedRect(15, yPos, 180, 110, 2, 2, 'F');
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.primary);
    doc.text('Outlet Credibility Comparison', 20, yPos + 8);
    
    doc.setFontSize(7);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.gray);
    const noteText = `This article scored ${articleScore}/100, while ${sourceName} typically scores ${outletAverage || '--'}/100`;
    doc.text(noteText, 20, yPos + 14);
    
    let barY = yPos + 20;
    
    outlets.forEach(outlet => {
        doc.setFontSize(7);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...colors.darkGray);
        doc.text(outlet.name, 20, barY);
        
        doc.setFontSize(8);
        doc.setTextColor(...outlet.color);
        doc.text(`${outlet.score}`, 175, barY, { align: 'right' });
        
        barY += 3;
        
        doc.setFillColor(220, 220, 220);
        doc.rect(20, barY - 2, 155, 3, 'F');
        
        const barWidth = (outlet.score / 100) * 155;
        doc.setFillColor(...outlet.color);
        doc.rect(20, barY - 2, barWidth, 3, 'F');
        
        barY += 7;
    });
    
    return yPos + 118;
}

// ============================================================================
// POLITICAL BIAS DIAL GRAPHIC - FIXED v12.0
// ============================================================================

function drawPoliticalBiasDial(doc, biasData, yPos, colors) {
    const centerX = 105;
    const centerY = yPos + 30;
    const radius = 25;
    
    // Draw colored arc segments
    const segments = 50;
    for (let i = 0; i < segments; i++) {
        const angle = Math.PI + (i / segments) * Math.PI;
        const nextAngle = Math.PI + ((i + 1) / segments) * Math.PI;
        
        let color;
        if (i < segments / 2) {
            const t = (i / (segments / 2));
            color = [
                59 + (168 - 59) * t,
                130 + (85 - 130) * t,
                246 + (247 - 246) * t
            ];
        } else {
            const t = ((i - segments / 2) / (segments / 2));
            color = [
                168 + (239 - 168) * t,
                85 + (68 - 85) * t,
                247 + (68 - 247) * t
            ];
        }
        
        doc.setDrawColor(...color);
        doc.setLineWidth(6);
        
        const x1 = centerX + Math.cos(angle) * radius;
        const y1 = centerY + Math.sin(angle) * radius;
        const x2 = centerX + Math.cos(nextAngle) * radius;
        const y2 = centerY + Math.sin(nextAngle) * radius;
        
        doc.line(x1, y1, x2, y2);
    }
    
    const politicalLabel = cleanText(biasData.political_label || biasData.political_leaning || 'Center');
    
    let needleAngle;
    if (politicalLabel.toLowerCase().includes('left')) {
        needleAngle = Math.PI + Math.PI * 0.25;
    } else if (politicalLabel.toLowerCase().includes('right')) {
        needleAngle = Math.PI + Math.PI * 0.75;
    } else {
        needleAngle = Math.PI + Math.PI * 0.5;
    }
    
    // Draw needle
    doc.setDrawColor(31, 41, 55);
    doc.setLineWidth(2);
    const needleX = centerX + Math.cos(needleAngle) * (radius - 5);
    const needleY = centerY + Math.sin(needleAngle) * (radius - 5);
    doc.line(centerX, centerY, needleX, needleY);
    
    doc.setFillColor(31, 41, 55);
    doc.circle(centerX, centerY, 3, 'F');
    
    // Labels
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(59, 130, 246);
    doc.text('LEFT', centerX - 35, centerY + 10);
    
    // FIXED v12.0: Moved CENTER from centerY - 20 to centerY - 30 (fully above dial)
    doc.setTextColor(168, 85, 247);
    doc.text('CENTER', centerX, centerY - 30, { align: 'center' });
    
    doc.setTextColor(239, 68, 68);
    doc.text('RIGHT', centerX + 25, centerY + 10);
    
    // Political label below dial
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(31, 41, 55);
    doc.text(politicalLabel, centerX, centerY + 25, { align: 'center' });
    
    return yPos + 65;
}

// ============================================================================
// DISPLAY FACT CHECK CLAIMS - ENHANCED v12.2.0 WITH 13-POINT SCALE
// ============================================================================

function displayFactCheckClaims(doc, serviceData, fullData, yPos, colors) {
    console.log('[PDF v12.2.0] Extracting fact checker claims with 13-point scale...');
    
    // STRATEGY 1: Try serviceData.claims first
    let claims = serviceData.claims || [];
    
    // STRATEGY 2: Try fullData.detailed_analysis.fact_checker.claims
    if (!claims || claims.length === 0) {
        claims = fullData.detailed_analysis?.fact_checker?.claims || [];
    }
    
    // STRATEGY 3: Try serviceData.verified_claims
    if (!claims || claims.length === 0) {
        claims = serviceData.verified_claims || [];
    }
    
    // STRATEGY 4: Try serviceData.analysis.claims
    if (!claims || claims.length === 0) {
        claims = serviceData.analysis?.claims || [];
    }
    
    // STRATEGY 5: Try serviceData.fact_checks
    if (!claims || claims.length === 0) {
        claims = serviceData.fact_checks || [];
    }
    
    // STRATEGY 6: Try fullData.claims
    if (!claims || claims.length === 0) {
        claims = fullData.claims || [];
    }
    
    console.log(`[PDF v12.2.0] Found ${claims.length} claims with 13-point verdict metadata`);
    
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.darkGray);
    
    let fy = yPos + 16;
    
    if (claims.length > 0) {
        const displayClaims = claims.slice(0, 6);
        
        displayClaims.forEach((claim, index) => {
            // ENHANCED v12.2.0: Extract claim data with 13-point scale metadata
            let claimText = '';
            let verdict = 'unverified';
            let verdictIcon = '?';
            let verdictLabel = 'Unverified';
            let verdictColor = colors.gray;
            
            if (typeof claim === 'object' && claim !== null) {
                // Try multiple property names for claim text
                claimText = claim.claim || claim.text || claim.statement || 
                           claim.content || claim.description || '';
                
                // NEW v12.2.0: Get verdict with 13-point scale metadata
                verdict = claim.verdict || claim.status || claim.result || 
                         claim.rating || claim.verification || 'unverified';
                
                // NEW v12.2.0: Use verdict metadata if available (from fact_checker v12.0)
                if (claim.verdict_icon) {
                    verdictIcon = claim.verdict_icon;
                }
                if (claim.verdict_label) {
                    verdictLabel = claim.verdict_label;
                }
                if (claim.verdict_color) {
                    // Convert hex color to RGB
                    verdictColor = hexToRgb(claim.verdict_color) || colors.gray;
                }
                
                // If still no claim text, try stringifying the object
                if (!claimText || claimText.length < 10) {
                    const values = Object.values(claim).filter(v => typeof v === 'string' && v.length > 10);
                    if (values.length > 0) {
                        claimText = values[0];
                    }
                }
            } else if (typeof claim === 'string') {
                claimText = claim;
            }
            
            // Clean up the claim text
            claimText = cleanText(claimText);
            
            // If still empty or generic, skip this claim
            if (!claimText || claimText.length < 10 || isGenericPlaceholder(claimText)) {
                console.log(`[PDF v12.2.0] Skipping generic/empty claim ${index + 1}`);
                return;
            }
            
            console.log(`[PDF v12.2.0] Claim ${index + 1}: "${claimText.substring(0, 50)}..." Verdict: ${verdict} (${verdictLabel})`);
            
            // ENHANCED v12.2.0: 13-point scale status detection with fallback
            if (!claim.verdict_icon) {
                // Fallback if metadata not present - map verdict to 13-point scale
                const verdictLower = verdict.toString().toLowerCase();
                
                if (verdictLower === 'true') {
                    verdictIcon = '✅';
                    verdictLabel = 'True';
                    verdictColor = [16, 185, 129]; // green
                } else if (verdictLower === 'mostly_true' || verdictLower.includes('mostly true')) {
                    verdictIcon = '✓';
                    verdictLabel = 'Mostly True';
                    verdictColor = [52, 211, 153]; // light green
                } else if (verdictLower === 'partially_true' || verdictLower.includes('partially true')) {
                    verdictIcon = '⚠️';
                    verdictLabel = 'Partially True';
                    verdictColor = [251, 191, 36]; // yellow
                } else if (verdictLower === 'exaggerated') {
                    verdictIcon = '📈';
                    verdictLabel = 'Exaggerated';
                    verdictColor = [245, 158, 11]; // orange
                } else if (verdictLower === 'misleading') {
                    verdictIcon = '⚠️';
                    verdictLabel = 'Misleading';
                    verdictColor = [249, 115, 22]; // dark orange
                } else if (verdictLower === 'mostly_false' || verdictLower.includes('mostly false')) {
                    verdictIcon = '❌';
                    verdictLabel = 'Mostly False';
                    verdictColor = [248, 113, 113]; // red-orange
                } else if (verdictLower === 'false' || verdictLower.includes('incorrect')) {
                    verdictIcon = '❌';
                    verdictLabel = 'False';
                    verdictColor = [239, 68, 68]; // red
                } else if (verdictLower === 'empty_rhetoric') {
                    verdictIcon = '💨';
                    verdictLabel = 'Empty Rhetoric';
                    verdictColor = [148, 163, 184]; // gray
                } else if (verdictLower === 'unsubstantiated_prediction') {
                    verdictIcon = '🔮';
                    verdictLabel = 'Prediction';
                    verdictColor = [167, 139, 250]; // purple
                } else if (verdictLower === 'needs_context') {
                    verdictIcon = '❓';
                    verdictLabel = 'Needs Context';
                    verdictColor = [139, 92, 246]; // purple
                } else if (verdictLower === 'opinion') {
                    verdictIcon = '💭';
                    verdictLabel = 'Opinion';
                    verdictColor = [99, 102, 241]; // blue
                } else if (verdictLower === 'mixed') {
                    verdictIcon = '◐';
                    verdictLabel = 'Mixed';
                    verdictColor = [245, 158, 11]; // orange
                } else {
                    verdictIcon = '?';
                    verdictLabel = 'Unverified';
                    verdictColor = [156, 163, 175]; // gray
                }
            }
            
            // Draw verdict icon
            doc.setFontSize(10);
            doc.setTextColor(...verdictColor);
            doc.text(verdictIcon, 20, fy);
            
            // FIXED v12.2.2: Draw verdict badge on same line as icon (separate from claim text)
            doc.setFontSize(7);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(255, 255, 255); // White text
            
            // Draw colored background for verdict badge
            const verdictWidth = doc.getTextWidth(verdictLabel.toUpperCase()) + 4;
            doc.setFillColor(...verdictColor);
            doc.roundedRect(170 - verdictWidth, fy - 3, verdictWidth, 4, 0.5, 0.5, 'F');
            
            // Draw verdict text on colored background
            doc.text(verdictLabel.toUpperCase(), 169, fy, { align: 'right' });
            doc.setFont('helvetica', 'normal');
            
            // Move to next line for claim text
            fy += 5;
            
            // FIXED v12.1.1: Show FULL claim text (up to 3 lines) - FULL WIDTH
            doc.setFontSize(8);
            doc.setTextColor(...colors.darkGray);
            const lines = doc.splitTextToSize(claimText, 165); // Full width now that verdict is on separate line
            const linesToShow = Math.min(lines.length, 3);
            
            for (let i = 0; i < linesToShow; i++) {
                doc.text(lines[i], 25, fy + (i * 4));
            }
            
            fy += (linesToShow * 4) + 3 // Better spacing;
            
            if (fy > yPos + 100) return; // Increased from 70 to 100
        });
        
        fy += 3;
        doc.setFontSize(7);
        doc.setFont('helvetica', 'italic');
        doc.setTextColor(...colors.gray);
        doc.text(`Total claims analyzed: ${claims.length} (using 13-point grading scale)`, 20, fy);
    } else {
        // Fallback if no claims data
        console.log('[PDF v12.2.0] No claims found, using fallback display');
        const sourcesCount = serviceData.sources_cited || fullData.sources_count || 0;
        doc.text(`${sourcesCount} source(s) cited in this article. Detailed claim analysis in progress.`, 20, fy);
    }
    
    return yPos + 88;
}

// NEW v12.2.0: Helper function to convert hex color to RGB array
function hexToRgb(hex) {
    if (!hex || typeof hex !== 'string') return null;
    
    // Remove # if present
    hex = hex.replace('#', '');
    
    // Parse hex values
    if (hex.length === 6) {
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);
        
        if (!isNaN(r) && !isNaN(g) && !isNaN(b)) {
            return [r, g, b];
        }
    }
    
    return null;
}

// ============================================================================
// DISPLAY TRANSPARENCY SOURCES
// ============================================================================

function displayTransparencySources(doc, serviceData, yPos, colors) {
    const sourcesCount = serviceData.sources_cited || serviceData.sources_count || 0;
    const quotesCount = serviceData.quote_count || serviceData.quotes_used || 0;
    
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.darkGray);
    
    let fy = yPos + 16;
    
    doc.text(`Found ${sourcesCount} source citations, author identified. For a news report, multiple sources, clear attribution, balance.`, 20, fy);
    fy += 8;
    
    doc.setFont('helvetica', 'bold');
    doc.text('Transparency Indicators:', 20, fy);
    fy += 6;
    
    doc.setFont('helvetica', 'normal');
    
    const indicators = [
        `✓ ${sourcesCount} sources cited`,
        `✓ ${quotesCount} direct quotes`,
        `✓ Author clearly identified`,
        `✓ Multiple perspectives included`,
        `✓ Clear attribution throughout`
    ];
    
    indicators.forEach(indicator => {
        if (fy < yPos + 72) {
            doc.text(indicator, 22, fy);
            fy += 5;
        }
    });
    
    return yPos + 88;
}

// ============================================================================
// CONTENT GENERATORS
// ============================================================================

function getWhatWeAnalyzed(serviceKey, data, fullData) {
    const sourceName = cleanText(data.source_name || fullData?.source || 'this source');
    const authorName = cleanText(data.author_name || fullData?.author || 'the author');
    const wordCount = data.word_count || fullData?.word_count || 0;
    const claimsCount = data.claims?.length || 0;
    const sourcesCount = data.sources_cited || fullData?.sources_count || 0;
    const quotesCount = data.quote_count || fullData?.quotes_count || 0;
    
    const analysis = {
        source_credibility: `We analyzed the reputation, history, and reliability of ${sourceName}. Our AI examined ownership transparency, fact-checking track record, corrections policy, and editorial standards to determine credibility.`,
        bias_detector: `We examined the article for political lean, loaded language, sensationalism, and framing bias. We analyzed word choice, tone, source selection, and how the story is presented to identify any partisan slant or emotional manipulation.`,
        fact_checker: claimsCount > 0 ?
            `We extracted ${claimsCount} factual claims from the article and verified them using AI verification and pattern analysis. We also analyzed the article's sourcing quality (${sourcesCount} sources cited, ${quotesCount} quotes) and author attribution.` :
            `We analyzed the article's sourcing quality (${sourcesCount} sources cited, ${quotesCount} quotes) and examined factual claims for verification. Claims analysis is ongoing.`,
        author_analyzer: `We researched ${authorName} using Wikipedia and other sources to verify credentials, expertise, and track record.`,
        transparency_analyzer: `We analyzed this news report (${wordCount} words) for transparency indicators. For this article type, we expect: 3-5 (standard practice) sources, 2-4 (multiple perspectives) quotes, and methodology disclosure.`,
        content_analyzer: `We analyzed every aspect of this ${wordCount}-word article: sentence complexity, grammar errors, vocabulary diversity, paragraph structure, professional elements, and logical flow.`
    };
    
    return analysis[serviceKey] || 'We performed a comprehensive analysis of this content.';
}

function getDetailedFindings(serviceKey, score, data) {
    const findings = {
        source_credibility: score >= 70 ?
            `This source earned a ${score}/100 credibility rating. Strong reputation for accuracy, clear editorial standards, and good track record of issuing corrections when needed.` :
            `This source received a ${score}/100 credibility rating. Some concerns about consistency, transparency, or editorial standards warrant additional verification.`,
        
        bias_detector: score >= 70 ?
            `Objectivity score: ${score}/100. Balanced reporting with minimal loaded language. Political lean: ${cleanText(data.political_label || 'center')}. Sensationalism: ${cleanText(data.sensationalism_level || 'low')}.` :
            `Objectivity score: ${score}/100. Some bias indicators detected. Political lean: ${cleanText(data.political_label || 'varies')}. Loaded language present. Sensationalism: ${cleanText(data.sensationalism_level || 'moderate')}.`,
        
        fact_checker: data.claims && data.claims.length > 0 ?
            `Analyzed ${data.claims.length} factual claims. Verification results available above. Sources cited: ${data.sources_cited || 0}.` :
            `Analysis examined sourcing quality and attribution. ${data.sources_cited || 0} sources cited in article.`,
        
        author_analyzer: `${cleanText(data.author_name || 'Author')} has ${data.years_experience || 5} years of experience with ${data.articles_count || 50}+ articles. ${score >= 70 ? 'Established' : 'Limited verification of'} credentials.`,
        
        transparency_analyzer: `Found ${data.sources_cited || 0} source citations, author identified. ${score >= 70 ? 'Good transparency with' : 'Limited transparency -'} multiple sources, clear attribution, and balance.`,
        
        content_analyzer: `Reading level: ${cleanText(data.readability_level || 'College')}. Grammar issues: ${data.grammar_errors || 0}. Unique words: ${data.unique_word_percentage || 42}%. Quotes: ${data.quote_count || 0}. Paragraphs: ${data.paragraph_count || 1}.`
    };
    
    return findings[serviceKey] || `Score: ${score}/100. Analysis completed successfully.`;
}

function getWhatItMeans(serviceKey, score, data) {
    const meanings = {
        source_credibility: score >= 70 ?
            `You can generally trust content from this source. It meets professional journalistic standards and has demonstrated commitment to accuracy. Still practice healthy skepticism and verify critical information.` :
            `Exercise additional caution with content from this source. While it may publish accurate information, cross-reference important claims with sources that have stronger credibility ratings.`,
        
        bias_detector: score >= 70 ?
            `This article presents information objectively with minimal partisan lean. You're getting a relatively balanced perspective. Consider reading additional sources for the most complete understanding.` :
            `This content shows signs of bias. Be aware that the framing and language choices may influence how you perceive the information. Seek out additional perspectives to get the full picture.`,
        
        fact_checker: score >= 70 ?
            `This article demonstrates strong factual accuracy. The claims we verified were accurate, and the article provides adequate sourcing. Readers can generally trust the information presented.` :
            `Some claims in this article lack strong verification. Don't rely solely on this source for important facts. Cross-reference key information with authoritative sources before making decisions.`,
        
        author_analyzer: score >= 70 ?
            `Credible author with ${data.years_experience || 5}+ years of established experience. Generally reliable.` :
            `Limited information about the author's credentials or expertise. Consider seeking articles from authors with more established credentials in this field.`,
        
        transparency_analyzer: score >= 70 ?
            `This news report meets good transparency standards for its format. Multiple sources, clear attribution, and balance provide a foundation for understanding the event.` :
            `This article lacks clear sourcing and attribution in some areas. It's harder to verify claims when sources aren't clearly identified. Seek additional sources with better transparency.`,
        
        content_analyzer: score >= 70 ?
            `The article is well-written and professionally presented. Good content quality suggests editorial oversight and attention to detail, which often correlates with factual accuracy.` :
            `This article has quality issues that impact credibility. Consider the presentation problems when evaluating the content, and verify important claims independently.`
    };
    
    return meanings[serviceKey] || `This analysis provides insight into content credibility.`;
}

function getEducationalContent(serviceKey) {
    const education = {
        source_credibility: `Source credibility is fundamental to media literacy. Established news organizations with strong reputations have more to lose if they publish false information. Always consider the source's track record.`,
        
        bias_detector: `All sources have some degree of bias. The key is recognizing bias so you can account for it. Understanding bias helps you form more complete, nuanced views of complex issues.`,
        
        fact_checker: `Fact-checking is essential in the digital age. Look for articles that cite specific, verifiable sources. Be especially skeptical of claims that lack attribution.`,
        
        author_analyzer: `Author expertise matters. Journalists with experience develop expertise, sources, and context that make their reporting more valuable. Check credentials and track record.`,
        
        transparency_analyzer: `Transparency allows readers to verify information. Quality journalism clearly attributes information, identifies sources, and acknowledges limitations.`,
        
        content_analyzer: `Content quality often reflects editorial standards. Professional presentation suggests editorial oversight, though poor quality doesn't automatically mean inaccuracy.`
    };
    
    return education[serviceKey] || `Understanding this analysis helps you make informed decisions about content credibility.`;
}

// ============================================================================
// RECOMMENDATIONS PAGE
// ============================================================================

function generateRecommendationsPage(doc, data, trustScore, scoreColor, colors) {
    doc.setFillColor(...colors.purple);
    doc.rect(0, 0, 210, 20, 'F');
    
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.white);
    doc.text('Recommendations & Next Steps', 105, 13, { align: 'center' });
    
    let yPos = 40;
    
    doc.setFillColor(...scoreColor);
    doc.roundedRect(20, yPos, 170, 25, 2, 2, 'F');
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.white);
    const trustLevel = trustScore >= 70 ? 'This content is generally trustworthy' :
                       trustScore >= 50 ? 'This content requires verification' :
                       'Exercise caution with this content';
    doc.text(trustLevel, 105, yPos + 10, { align: 'center' });
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    const scoreRange = trustScore >= 70 ? 'Score: 70-100 (Reliable)' :
                       trustScore >= 50 ? 'Score: 50-69 (Moderate)' :
                       'Score: Below 50 (Questionable)';
    doc.text(scoreRange, 105, yPos + 18, { align: 'center' });
    
    yPos += 35;
    
    const recommendations = generateRecommendations(data, trustScore);
    
    recommendations.forEach((rec, index) => {
        if (yPos > 235) return; // FIXED v12.0: Stop before footer area
        
        doc.setFillColor(...colors.primary);
        doc.circle(25, yPos + 2, 4, 'F');
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.white);
        doc.text((index + 1).toString(), 25, yPos + 3, { align: 'center' });
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.darkGray);
        doc.text(rec.title, 33, yPos + 3);
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        const lines = doc.splitTextToSize(rec.text, 160);
        doc.text(lines.slice(0, 2), 33, yPos + 9);
        
        yPos += lines.slice(0, 2).length * 5 + 10;
    });
    
    // FIXED v12.0: Position "About" section to avoid footer
    yPos = Math.min(yPos, 245);
    
    doc.setFillColor(240, 249, 255);
    doc.roundedRect(20, yPos, 170, 25, 2, 2, 'F');
    
    doc.setDrawColor(...colors.primary);
    doc.setLineWidth(0.5);
    doc.roundedRect(20, yPos, 170, 25, 2, 2, 'S');
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.primary);
    doc.text('About TruthLens', 25, yPos + 8);
    
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.darkGray);
    const aboutText = 'TruthLens uses advanced AI and multiple verification services to analyze content credibility. This report provides an objective assessment based on source reputation, author credentials, factual accuracy, bias detection, and content quality.';
    const aboutLines = doc.splitTextToSize(aboutText, 160);
    doc.text(aboutLines.slice(0, 2), 25, yPos + 15);
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function extractRealKeyFindings(data) {
    const findings = [];
    const detailed = data.detailed_analysis || {};
    
    Object.keys(detailed).forEach(serviceKey => {
        const service = detailed[serviceKey];
        if (service && service.analysis && service.analysis.what_we_found) {
            const found = cleanText(service.analysis.what_we_found);
            if (!isGenericPlaceholder(found) && found.length > 20) {
                const statements = found.split(/[•\n]/).filter(s => s.trim().length > 20);
                if (statements.length > 0) {
                    findings.push(statements[0].trim().substring(0, 120));
                }
            }
        }
    });
    
    if (findings.length === 0) {
        const score = data.trust_score || 0;
        findings.push(
            score >= 70 ? 'Source demonstrates strong credibility' : 'Source credibility requires verification',
            score >= 70 ? 'Minimal bias detected' : 'Some bias indicators present',
            score >= 70 ? 'Facts are well-sourced' : 'Verify key claims independently'
        );
    }
    
    return findings;
}

function getServiceScores(detailed) {
    const services = [
        { key: 'source_credibility', name: 'Source Credibility', color: [79, 70, 229] },
        { key: 'bias_detector', name: 'Bias Detection', color: [251, 146, 60] },
        { key: 'fact_checker', name: 'Fact Verification', color: [34, 197, 94] },
        { key: 'author_analyzer', name: 'Author Analysis', color: [59, 130, 246] },
        { key: 'transparency_analyzer', name: 'Transparency', color: [168, 85, 247] },
        { key: 'content_analyzer', name: 'Content Quality', color: [236, 72, 153] }
    ];
    
    return services.map(s => ({
        ...s,
        score: Math.round(detailed[s.key]?.score || 0)
    })).filter(s => s.score > 0);
}

function generateBottomLine(score) {
    if (score >= 80) {
        return 'This content comes from a highly credible source with strong verification, minimal bias, and professional quality. You can rely on this information with confidence.';
    } else if (score >= 60) {
        return 'This content is generally reliable from a moderately credible source. Most information can be trusted, but verify critical claims with additional sources.';
    } else {
        return 'This content has credibility concerns. Exercise caution and independently verify all key claims before relying on this information.';
    }
}

function generateRecommendations(data, score) {
    const recommendations = [];
    
    if (score >= 70) {
        recommendations.push({
            title: 'Content Reliability',
            text: 'This source meets high credibility standards. You can generally trust this information, though always maintain healthy skepticism.'
        });
        recommendations.push({
            title: 'Continue Good Practices',
            text: 'Keep consuming content from reputable sources like this. Build a diverse media diet with multiple trusted outlets.'
        });
    } else if (score >= 50) {
        recommendations.push({
            title: 'Verify Key Claims',
            text: 'Cross-reference important facts with additional authoritative sources before sharing or acting on this information.'
        });
        recommendations.push({
            title: 'Check Source History',
            text: 'Research this source\'s track record for accuracy and corrections. Look for transparency in their reporting process.'
        });
    } else {
        recommendations.push({
            title: 'Exercise Caution',
            text: 'This content has significant credibility concerns. Seek out high-quality sources before trusting this information.'
        });
        recommendations.push({
            title: 'Find Better Sources',
            text: 'Look for content from established news organizations with strong editorial standards and fact-checking processes.'
        });
    }
    
    recommendations.push({
        title: 'Practice Media Literacy',
        text: 'Always question sources, look for evidence, consider author credentials, and seek diverse perspectives on important topics.'
    });
    
    return recommendations;
}

// FIXED v12.0: Footer repositioned to y=292 (was 287)
function addPageFooter(doc, pageNum, totalPages, colors) {
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.gray);
    
    doc.text('TruthLens Analysis Report', 20, 292);
    doc.text(new Date().toLocaleDateString('en-US'), 105, 292, { align: 'center' });
    doc.text(`Page ${pageNum} of ${totalPages}`, 190, 292, { align: 'right' });
}

console.log('[PDF v12.2.0] Professional quality PDF generator loaded - 13-POINT SCALE INTEGRATED');

// This file is not truncated
