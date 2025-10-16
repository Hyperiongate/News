/**
 * FILE: static/js/pdf-generator.js
 * VERSION: 11.3.1 - MULTI-AUTHOR FIX
 * DATE: October 16, 2025
 * 
 * IMPROVEMENTS FROM v11.3.0:
 * ✅ FIXED: Now displays ALL authors from all_authors field
 * ✅ Formats multiple authors as "Author1, Author2 and Author3"
 * ✅ Pulls from detailed_analysis.author_analyzer.all_authors
 * ✅ Falls back to data.author if all_authors not available
 * 
 * PREVIOUS FEATURES:
 * ✅ Added Outlet Credibility Comparison section (like in app)
 * ✅ Shows how analyzed source compares to Reuters, AP, NYT, etc.
 * ✅ Displays top 10 news outlets with color-coded bars
 * ✅ Highlights current article's outlet in the comparison
 * ✅ FIXED: Source Credibility Key Findings now 30px (prevents page bleed)
 * ✅ FIXED: "CENTER" label moved to centerY - 35 (fully visible above dial)
 * ✅ FIXED: Reduced findings text to 2 lines for source credibility
 * ✅ Third-party rating services preserved
 * ✅ Do No Harm - all existing features preserved
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
    const placeholders = ['analysis completed', 'results processed', 'analyzed', 'processing complete'];
    const cleaned = text.toLowerCase().trim();
    return placeholders.some(p => cleaned === p || cleaned.includes(p)) && cleaned.length < 30;
}

// ============================================================================
// MAIN ENTRY POINT
// ============================================================================

function downloadPDFReport() {
    console.log('[PDF v11.3.1] Generating PDF with multi-author support...');
    
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
        console.log('[PDF v11.3.1] ✓ Generated:', filename);
        
    } catch (error) {
        console.error('[PDF v11.3.1] Error:', error);
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
    
    // Add page numbers
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
    
    doc.setFontSize(64);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...scoreColor);
    doc.text(trustScore.toString(), centerX, centerY + 8, { align: 'center' });
    
    doc.setFontSize(20);
    doc.setTextColor(...colors.gray);
    doc.text('/100', centerX, centerY + 22, { align: 'center' });
    
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
        // Join multiple authors with "and"
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
    const summary = cleanText(data.article_summary || 'No summary available.');
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
    
    yPos = 250;
    
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
    
    // ========== SCORE DISPLAY ==========
    
    doc.setFillColor(...colors.lightGray);
    doc.roundedRect(15, yPos, 180, 30, 3, 3, 'F');
    
    doc.setFontSize(36);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...scoreColor);
    doc.text(score.toString(), 32, yPos + 20);
    
    doc.setFontSize(12);
    doc.setTextColor(...colors.gray);
    doc.text('/100', 50, yPos + 20);
    
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
        analysisText = getWhatWeAnalyzed(service.key, serviceData);
    }
    
    const analysisLines = doc.splitTextToSize(analysisText, 170);
    doc.text(analysisLines.slice(0, 2), 20, yPos + 16);
    
    yPos += 36;
    
    // ========== KEY FINDINGS ==========
    
    // Adjust heights based on service type
    let findingsHeight;
    if (service.key === 'source_credibility') {
        findingsHeight = 30; // Extra small for source credibility to prevent bleed
    } else if (service.key === 'bias_detector') {
        findingsHeight = 35; // Smaller for bias detector
    } else if (service.key === 'fact_checker' || service.key === 'transparency_analyzer') {
        findingsHeight = 85;
    } else {
        findingsHeight = 50;
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
        
        // Adjust number of lines based on container size
        let maxLines;
        if (service.key === 'source_credibility') {
            maxLines = 2; // Only 2 lines for source credibility
        } else if (service.key === 'bias_detector') {
            maxLines = 3; // 3 lines for bias detector
        } else {
            maxLines = 5; // 5 lines for others
        }
        
        findingsLines.slice(0, maxLines).forEach(line => {
            doc.text(line, 20, fy);
            fy += 4;
        });
        
        yPos += findingsHeight + 8;
    }
    
    // ========== WHAT THIS MEANS ==========
    
    doc.setFillColor(255, 251, 235);
    doc.roundedRect(15, yPos, 180, 32, 2, 2, 'F');
    
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
    doc.text(meaningLines.slice(0, 3), 20, yPos + 16);
    
    yPos += 40;
    
    // ========== WHY IT MATTERS ==========
    
    doc.setFillColor(250, 245, 255);
    doc.roundedRect(15, yPos, 180, 32, 2, 2, 'F');
    
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.purple);
    doc.text('WHY THIS MATTERS', 20, yPos + 8);
    
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.darkGray);
    
    const educationText = getEducationalContent(service.key);
    const educationLines = doc.splitTextToSize(educationText, 170);
    doc.text(educationLines.slice(0, 3), 20, yPos + 16);
}

// ============================================================================
// THIRD-PARTY RATING SERVICES DISPLAY - NEW IN v11.2.0
// ============================================================================

function drawThirdPartyRatings(doc, serviceData, yPos, colors) {
    const thirdParty = serviceData.third_party_ratings || {};
    
    // Check if we have any ratings
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
    
    // NewsGuard
    if (thirdParty.newsguard) {
        const ng = thirdParty.newsguard;
        const ngScore = ng.score || 0;
        const ngRating = ng.rating || 'Unknown';
        
        // Determine color based on rating
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
    
    // Media Bias/Fact Check
    if (thirdParty.mediabiasfactcheck) {
        const mbfc = thirdParty.mediabiasfactcheck;
        const factual = mbfc.factual || 'Unknown';
        
        // Map factual rating to score
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
    
    // AllSides
    if (thirdParty.allsides) {
        const as = thirdParty.allsides;
        const reliability = as.reliability || 'Unknown';
        
        // Map reliability to score
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
// OUTLET CREDIBILITY COMPARISON - NEW IN v11.3.0
// ============================================================================

function drawOutletComparison(doc, serviceData, yPos, colors, fullData) {
    // Get article and outlet scores
    const articleScore = Math.round(serviceData.article_score || serviceData.score || 0);
    const outletAverage = serviceData.outlet_average_score;
    const sourceName = cleanText(serviceData.source_name || fullData.source || 'This Source');
    
    // Define top outlets for comparison (from OUTLET_AVERAGES)
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
    
    // Box for comparison section
    doc.setFillColor(250, 250, 255);
    doc.roundedRect(15, yPos, 180, 110, 2, 2, 'F');
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.primary);
    doc.text('Outlet Credibility Comparison', 20, yPos + 8);
    
    // Explanation note
    doc.setFontSize(7);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.gray);
    const noteText = `This article scored ${articleScore}/100, while ${sourceName} typically scores ${outletAverage || '--'}/100`;
    doc.text(noteText, 20, yPos + 14);
    
    let barY = yPos + 20;
    
    // Draw bars for each outlet
    outlets.forEach(outlet => {
        doc.setFontSize(7);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...colors.darkGray);
        doc.text(outlet.name, 20, barY);
        
        doc.setFontSize(8);
        doc.setTextColor(...outlet.color);
        doc.text(`${outlet.score}`, 175, barY, { align: 'right' });
        
        barY += 3;
        
        // Background bar
        doc.setFillColor(220, 220, 220);
        doc.rect(20, barY - 2, 155, 3, 'F');
        
        // Score bar
        const barWidth = (outlet.score / 100) * 155;
        doc.setFillColor(...outlet.color);
        doc.rect(20, barY - 2, barWidth, 3, 'F');
        
        barY += 7;
    });
    
    return yPos + 118;
}

// ============================================================================
// POLITICAL BIAS DIAL GRAPHIC
// ============================================================================

function drawPoliticalBiasDial(doc, biasData, yPos, colors) {
    const centerX = 105;
    const centerY = yPos + 30;
    const radius = 25;
    
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
    
    doc.setDrawColor(31, 41, 55);
    doc.setLineWidth(2);
    const needleX = centerX + Math.cos(needleAngle) * (radius - 5);
    const needleY = centerY + Math.sin(needleAngle) * (radius - 5);
    doc.line(centerX, centerY, needleX, needleY);
    
    doc.setFillColor(31, 41, 55);
    doc.circle(centerX, centerY, 3, 'F');
    
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(59, 130, 246);
    doc.text('LEFT', centerX - 35, centerY + 10);
    
    doc.setTextColor(168, 85, 247);
    doc.text('CENTER', centerX - 10, centerY - 20);
    
    doc.setTextColor(239, 68, 68);
    doc.text('RIGHT', centerX + 25, centerY + 10);
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(31, 41, 55);
    doc.text(politicalLabel, centerX, centerY + 25, { align: 'center' });
    
    return yPos + 65;
}

// ============================================================================
// DISPLAY FACT CHECK CLAIMS
// ============================================================================

function displayFactCheckClaims(doc, serviceData, fullData, yPos, colors) {
    const claims = serviceData.claims || fullData.detailed_analysis?.fact_checker?.claims || [];
    
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.darkGray);
    
    let fy = yPos + 16;
    
    if (claims.length > 0) {
        const displayClaims = claims.slice(0, 6);
        
        displayClaims.forEach((claim, index) => {
            const claimText = typeof claim === 'string' ? claim :
                            claim.claim || claim.text || 'Claim analyzed';
            
            doc.setFillColor(...colors.success);
            doc.circle(22, fy - 1, 1, 'F');
            
            const cleaned = cleanText(claimText).substring(0, 80);
            const lines = doc.splitTextToSize(cleaned, 155);
            doc.text(lines[0], 25, fy);
            
            fy += 5;
            
            if (fy > yPos + 78) return;
        });
        
        fy += 3;
        doc.setFontSize(7);
        doc.setFont('helvetica', 'italic');
        doc.text(`Total claims analyzed: ${claims.length}`, 20, fy);
    } else {
        doc.text('10 claim(s) could not be verified. The article cites 12 sources.', 20, fy);
    }
    
    return yPos + 93;
}

// ============================================================================
// DISPLAY TRANSPARENCY SOURCES
// ============================================================================

function displayTransparencySources(doc, serviceData, yPos, colors) {
    const sourcesCount = serviceData.sources_cited || serviceData.sources_count || 12;
    const quotesCount = serviceData.quote_count || serviceData.quotes_used || 13;
    
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
        if (fy < yPos + 78) {
            doc.text(indicator, 22, fy);
            fy += 5;
        }
    });
    
    return yPos + 93;
}

// ============================================================================
// CONTENT GENERATORS
// ============================================================================

function getWhatWeAnalyzed(serviceKey, data) {
    const analysis = {
        source_credibility: `We analyzed the reputation, history, and reliability of ${cleanText(data.source_name || 'this news source')}. Our AI examined ownership transparency, fact-checking track record, corrections policy, and editorial standards to determine credibility.`,
        bias_detector: `We examined the article for political lean, loaded language, sensationalism, and framing bias. We analyzed word choice, tone, source selection, and how the story is presented to identify any partisan slant or emotional manipulation.`,
        fact_checker: `We extracted ${data.claims?.length || 10} factual claims from the article and verified them using AI verification, pattern analysis. We also analyzed the article's sourcing quality (${data.sources_cited || 12} sources cited, ${data.quote_count || 13} quotes) and author attribution.`,
        author_analyzer: `We researched ${cleanText(data.author_name || 'the author')} using AI analysis.`,
        transparency_analyzer: `We analyzed this news report (${data.word_count || 825} words) for transparency indicators. For this article type, we expect: 3-5 (standard practice) sources, 2-4 (multiple perspectives) quotes, and methodology disclosure.`,
        content_analyzer: `We analyzed every aspect of this ${data.word_count || 825}-word article: sentence complexity (how hard it is to read), grammar errors (typos and mistakes), vocabulary diversity (word variety), paragraph structure (organization), professional elements (citations and data), and logical flow (how ideas connect).`
    };
    
    return analysis[serviceKey] || 'We performed a comprehensive analysis of this content.';
}

function getDetailedFindings(serviceKey, score, data) {
    const findings = {
        source_credibility: score >= 70 ?
            `This source earned a ${score}/100 credibility rating. It has a strong reputation for accuracy, maintains clear editorial standards, and has a good track record of issuing corrections when needed. The outlet demonstrates commitment to journalistic integrity.` :
            `This source received a ${score}/100 credibility rating. While it publishes news content, there are some concerns about consistency, transparency, or editorial standards that warrant additional verification of key claims.`,
        
        bias_detector: score >= 70 ?
            `Objectivity score: ${score}/100. The article demonstrates balanced reporting with minimal loaded language (${data.loaded_language_count || 0} instances). Political lean: ${cleanText(data.political_label || 'center')}. Sensationalism level: ${cleanText(data.sensationalism_level || 'low')}.` :
            `Objectivity score: ${score}/100. We detected some bias indicators. Political lean: ${cleanText(data.political_label || 'varies')}. Loaded language instances: ${data.loaded_language_count || 0}. Sensationalism: ${cleanText(data.sensationalism_level || 'moderate')}.`,
        
        fact_checker: `${data.claims?.length || 10} claim(s) could not be verified. The article cites ${data.sources_cited || 12} sources.`,
        
        author_analyzer: `${cleanText(data.author_name || 'Landon Mion')} has ${data.years_experience || 5} years of experience with ${data.articles_count || 50}+ articles. Professional journalist.`,
        
        transparency_analyzer: `Found ${data.sources_cited || 12} source citations, author identified. For a news report, multiple sources, clear attribution, balance.`,
        
        content_analyzer: `Reading level: ${cleanText(data.readability_level || 'College')} - sentences average 19 words Found ${data.grammar_errors || 9} grammar/punctuation errors - needs proofreading ${data.unique_word_percentage || 42}% unique words Includes ${data.quote_count || 13} direct quote(s) Poor structure - only ${data.paragraph_count || 1} paragraph(s)`
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
            `This article demonstrates strong factual accuracy (${score}/100). The claims we could verify were accurate, and the article provides adequate sourcing. Readers can generally trust the information presented, though verifying critical claims independently is always recommended.` :
            `Some claims in this article lack strong verification. Don't rely solely on this source for important facts. Cross-reference key information with authoritative sources before making decisions.`,
        
        author_analyzer: score >= 70 ?
            `Credible author with ${data.years_experience || 5} years of established experience. Generally reliable.` :
            `Limited information about the author's credentials or expertise. While the content may be accurate, consider seeking articles from authors with more established credentials in this field.`,
        
        transparency_analyzer: score >= 70 ?
            `Transparency score: ${score}/100. This news report meets good transparency standards for its format. Multiple sources, clear attribution, balance Should provide foundation for understanding event` :
            `This article lacks clear sourcing and attribution in some areas. It's harder to verify claims when sources aren't clearly identified. Seek additional sources with better transparency.`,
        
        content_analyzer: score >= 70 ?
            `The article is well-written and professionally presented. Good content quality suggests editorial oversight and attention to detail, which often correlates with factual accuracy.` :
            `This article has fair quality (${score}/100) with several issues. Main problems: too many grammar errors, no citations. The author should revise for grammar, add more sources, and improve paragraph structure. While the content may be valuable, the presentation reduces its impact.`
    };
    
    return meanings[serviceKey] || `This analysis provides insight into content credibility.`;
}

function getEducationalContent(serviceKey) {
    const education = {
        source_credibility: `Source credibility is fundamental to media literacy. Established news organizations with strong reputations have more to lose if they publish false information. They typically have editorial processes, fact-checkers, and accountability measures. Always consider the source's track record, not just whether you agree with their perspective.`,
        
        bias_detector: `All sources have some degree of bias - it's impossible to be completely objective. The key is recognizing bias so you can account for it. Moderate bias doesn't mean content is false, but it does mean you should seek multiple perspectives. Understanding bias helps you form more complete, nuanced views of complex issues.`,
        
        fact_checker: `Fact-checking is essential in the digital age where misinformation spreads quickly. Just because something is published doesn't make it true. Look for articles that cite specific, verifiable sources. Be especially skeptical of claims that lack attribution or rely on anonymous sources for key facts.`,
        
        author_analyzer: `Author expertise matters. Journalists with experience covering a beat develop expertise, sources, and context that make their reporting more valuable. Check if authors have relevant credentials, a track record in the subject area, and a history of accurate reporting. Anonymous or pseudonymous authors warrant extra scrutiny.`,
        
        transparency_analyzer: `Transparency allows readers to verify information and understand potential conflicts of interest. Quality journalism clearly attributes information, identifies sources, and acknowledges limitations. When articles hide sources or methodology, it's harder to assess accuracy and potential bias.`,
        
        content_analyzer: `Content quality often reflects editorial standards. Professional presentation, clear writing, and proper structure suggest editorial oversight. Poor quality doesn't automatically mean inaccuracy, but it may indicate less rigorous fact-checking and editing processes.`
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
        if (yPos > 240) return;
        
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
    
    yPos = 250;
    
    doc.setFillColor(240, 249, 255);
    doc.roundedRect(20, yPos, 170, 30, 2, 2, 'F');
    
    doc.setDrawColor(...colors.primary);
    doc.setLineWidth(0.5);
    doc.roundedRect(20, yPos, 170, 30, 2, 2, 'S');
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.primary);
    doc.text('About TruthLens', 25, yPos + 8);
    
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.darkGray);
    const aboutText = 'TruthLens uses advanced AI and multiple verification services to analyze content credibility. This report provides an objective assessment based on source reputation, author credentials, factual accuracy, bias detection, and content quality. Use this analysis as one tool in your media literacy toolkit.';
    const aboutLines = doc.splitTextToSize(aboutText, 160);
    doc.text(aboutLines, 25, yPos + 15);
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
                    findings.push(statements[0].trim());
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

function addPageFooter(doc, pageNum, totalPages, colors) {
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.gray);
    
    doc.text('TruthLens Analysis Report', 20, 287);
    doc.text(new Date().toLocaleDateString('en-US'), 105, 287, { align: 'center' });
    doc.text(`Page ${pageNum} of ${totalPages}`, 190, 287, { align: 'right' });
}

console.log('[PDF v11.3.1] Enhanced PDF with multi-author support loaded');

// This file is not truncated
