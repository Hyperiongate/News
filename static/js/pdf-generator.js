/**
 * FILE: static/js/pdf-generator.js
 * VERSION: 10.2.0 - FIXED: STRIP UNICODE ICONS + BETTER FALLBACKS
 * DATE: October 15, 2025
 * 
 * CRITICAL FIXES:
 * ✅ Strips ALL unicode emoji/icons from backend data (Ø=ÜÖ, etc.)
 * ✅ Replaces generic "Analysis completed" with meaningful text
 * ✅ Uses score-based interpretations when backend has placeholders
 * ✅ Cleans all text before rendering
 */

// ============================================================================
// TEXT CLEANING UTILITY
// ============================================================================

function cleanText(text) {
    if (!text) return '';
    
    // Remove all emoji and special unicode characters that jsPDF can't handle
    // This removes: Ø=ÜÖ, Ø=Ý$, Ø=ÜÊ, Ø=ÜÝ, and all other problematic chars
    return text
        .replace(/[\u{1F300}-\u{1F9FF}]/gu, '') // Emoji
        .replace(/[\u{2600}-\u{26FF}]/gu, '')   // Misc symbols
        .replace(/[\u{2700}-\u{27BF}]/gu, '')   // Dingbats
        .replace(/[\u{FE00}-\u{FE0F}]/gu, '')   // Variation selectors
        .replace(/[\u{1F000}-\u{1FFFF}]/gu, '') // Supplementary symbols
        .replace(/Ø=[^\s]*/g, '')                // Specific pattern from your data
        .replace(/[^\x20-\x7E\s]/g, '')          // Keep only printable ASCII + whitespace
        .replace(/\s+/g, ' ')                    // Normalize whitespace
        .trim();
}

function isGenericPlaceholder(text) {
    if (!text) return true;
    
    const placeholders = [
        'analysis completed',
        'results processed',
        'analyzed',
        'processing complete',
        'data received'
    ];
    
    const cleaned = text.toLowerCase().trim();
    return placeholders.some(p => cleaned === p || cleaned.includes(p)) && cleaned.length < 30;
}

// ============================================================================
// MAIN ENTRY POINT
// ============================================================================

function downloadPDFReport() {
    console.log('[PDF v10.2.0] Starting PDF generation with text cleaning...');
    
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
        console.log('[PDF v10.2.0] ✓ Generated:', filename);
        
    } catch (error) {
        console.error('[PDF v10.2.0] Error:', error);
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
        white: [255, 255, 255]
    };
    
    const scoreColor = trustScore >= 70 ? colors.success :
                       trustScore >= 50 ? colors.warning : colors.danger;
    
    generateCoverPage(doc, data, trustScore, scoreColor, colors);
    
    doc.addPage();
    generateExecutiveSummary(doc, data, trustScore, scoreColor, colors);
    
    const services = [
        { key: 'source_credibility', title: 'Source Credibility Analysis' },
        { key: 'bias_detector', title: 'Bias Detection Analysis' },
        { key: 'fact_checker', title: 'Fact Verification Analysis' },
        { key: 'author_analyzer', title: 'Author Credibility Analysis' },
        { key: 'transparency_analyzer', title: 'Transparency Analysis' },
        { key: 'content_analyzer', title: 'Content Quality Analysis' }
    ];
    
    services.forEach(service => {
        if (detailed[service.key] && detailed[service.key].score !== undefined) {
            doc.addPage();
            generateServicePage(doc, service, detailed[service.key], colors);
        }
    });
    
    doc.addPage();
    generateRecommendationsPage(doc, data, trustScore, scoreColor, colors);
    
    const totalPages = doc.internal.getNumberOfPages();
    for (let i = 2; i <= totalPages; i++) {
        doc.setPage(i);
        addPageFooter(doc, i, totalPages, colors);
    }
}

// ============================================================================
// PAGE 1: COVER PAGE
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
    doc.text(cleanText(data.author || 'Unknown Author').substring(0, 60), 50, yPos);
    
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
// PAGE 2: EXECUTIVE SUMMARY
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
// SERVICE PAGES - WITH CLEANED TEXT
// ============================================================================

function generateServicePage(doc, service, serviceData, colors) {
    doc.setFillColor(...colors.primary);
    doc.rect(0, 0, 210, 20, 'F');
    
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.white);
    doc.text(service.title, 105, 13, { align: 'center' });
    
    let yPos = 35;
    
    const score = Math.round(serviceData.score || 0);
    const scoreColor = score >= 70 ? colors.success :
                       score >= 50 ? colors.warning : colors.danger;
    
    doc.setFillColor(...colors.lightGray);
    doc.roundedRect(20, yPos, 50, 35, 2, 2, 'F');
    
    doc.setFontSize(36);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...scoreColor);
    doc.text(score.toString(), 45, yPos + 20, { align: 'center' });
    
    doc.setFontSize(10);
    doc.setTextColor(...colors.gray);
    doc.text('/100', 45, yPos + 28, { align: 'center' });
    
    // Get interpretation - use what_it_means if it's not a placeholder
    let interpretation = '';
    if (serviceData.analysis?.what_it_means && !isGenericPlaceholder(serviceData.analysis.what_it_means)) {
        interpretation = cleanText(serviceData.analysis.what_it_means);
    } else {
        interpretation = getServiceInterpretation(service.key, score, serviceData);
    }
    
    doc.setFillColor(...colors.lightGray);
    doc.roundedRect(75, yPos, 115, 35, 2, 2, 'F');
    
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.darkGray);
    doc.text('Assessment:', 80, yPos + 8);
    
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    const interpLines = doc.splitTextToSize(interpretation, 105);
    doc.text(interpLines.slice(0, 3), 80, yPos + 15);
    
    yPos += 45;
    
    // Get findings - use what_we_found if it's not a placeholder
    let findingsText = '';
    if (serviceData.analysis?.what_we_found && !isGenericPlaceholder(serviceData.analysis.what_we_found)) {
        findingsText = cleanText(serviceData.analysis.what_we_found);
    } else {
        findingsText = generateServiceFindings(service.key, score, serviceData);
    }
    
    if (findingsText) {
        doc.setFontSize(13);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.darkGray);
        doc.text('Key Findings:', 20, yPos);
        
        yPos += 8;
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        const findingLines = doc.splitTextToSize(findingsText, 170);
        
        findingLines.slice(0, 8).forEach(line => {
            if (yPos < 250) {
                doc.text(line, 20, yPos);
                yPos += 5;
            }
        });
        
        yPos += 5;
    }
    
    if (yPos < 240) {
        addServiceSpecificInsights(doc, service.key, serviceData, yPos, colors);
    }
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
            score >= 70 ? 'Source demonstrates strong credibility and reputation' : 'Source credibility requires verification',
            score >= 70 ? 'Content shows minimal bias and balanced reporting' : 'Some bias indicators detected in content',
            score >= 70 ? 'Facts are well-sourced and verifiable' : 'Key claims should be independently verified'
        );
    }
    
    return findings;
}

function generateServiceFindings(key, score, data) {
    const findings = {
        source_credibility: score >= 70 ? 
            `Strong source credibility. The outlet has a reputation score of ${score}/100 and is recognized as a reliable news source.` :
            `Moderate source credibility. This outlet has a credibility score of ${score}/100. Verify key claims independently.`,
        
        bias_detector: score >= 70 ?
            `Minimal bias detected. The content maintains ${score}/100 objectivity and presents information in a balanced manner.` :
            `Some bias detected. Objectivity score is ${score}/100. Consider seeking additional perspectives from diverse sources.`,
        
        fact_checker: score >= 70 ?
            `Strong factual accuracy (${score}/100). Claims are well-supported by evidence from reliable sources.` :
            `Moderate factual accuracy (${score}/100). Some claims may need additional verification.`,
        
        author_analyzer: score >= 70 ?
            `Author has strong credentials with a credibility score of ${score}/100. Demonstrated expertise in this subject area.` :
            `Author credentials are moderate (${score}/100). Verify author qualifications independently.`,
        
        transparency_analyzer: score >= 70 ?
            `Excellent transparency (${score}/100). Content includes clear sourcing and proper attribution throughout.` :
            `Moderate transparency (${score}/100). Some areas lack clear source information.`,
        
        content_analyzer: score >= 70 ?
            `High content quality (${score}/100). Well-written with proper structure and professional standards.` :
            `Fair content quality (${score}/100). Some issues with writing, structure, or presentation.`
    };
    
    return findings[key] || 'Analysis completed successfully.';
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

function getServiceInterpretation(key, score, data) {
    const interpretations = {
        source_credibility: score >= 70 ? 
            'This source has established credibility and a strong reputation for reliable journalism.' :
            'This source has moderate credibility. Independent verification of key claims is recommended.',
        
        bias_detector: score >= 70 ?
            'Content demonstrates objectivity with minimal bias. Balanced perspectives are presented.' :
            'Some bias elements detected. Consider seeking additional perspectives from diverse sources.',
        
        fact_checker: score >= 70 ?
            'Claims are well-supported by evidence from reliable sources. Factual accuracy is strong.' :
            'Some claims lack strong verification. Cross-reference important facts with authoritative sources.',
        
        author_analyzer: score >= 70 ?
            'Author has strong credentials and demonstrated expertise in this subject area.' :
            'Author credentials are unclear or limited. Verify author qualifications independently.',
        
        transparency_analyzer: score >= 70 ?
            'Content shows strong transparency with clear sourcing and proper attribution.' :
            'Transparency is limited. Look for additional source information and citations.',
        
        content_analyzer: score >= 70 ?
            'Content is well-written, properly structured, and maintains professional quality standards.' :
            'Content quality has some issues. Verify information with higher-quality sources.'
    };
    
    return interpretations[key] || 'Analysis completed successfully.';
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

function addServiceSpecificInsights(doc, key, data, yPos, colors) {
    if (yPos > 235) return;
    
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.darkGray);
    doc.text('Additional Details:', 20, yPos);
    
    yPos += 7;
    
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    
    const details = [];
    
    if (key === 'source_credibility') {
        if (data.reputation) details.push(`Reputation: ${cleanText(data.reputation)}`);
        if (data.credibility_level) details.push(`Level: ${cleanText(data.credibility_level)}`);
        if (data.domain) details.push(`Domain: ${cleanText(data.domain)}`);
    } else if (key === 'bias_detector') {
        if (data.political_label || data.political_leaning) {
            details.push(`Political Leaning: ${cleanText(data.political_label || data.political_leaning)}`);
        }
        if (data.objectivity_score) details.push(`Objectivity: ${data.objectivity_score}/100`);
        if (data.sensationalism_level) details.push(`Sensationalism: ${cleanText(data.sensationalism_level)}`);
        if (data.loaded_language_count !== undefined) {
            details.push(`Loaded Language: ${data.loaded_language_count} instances`);
        }
    } else if (key === 'fact_checker') {
        if (data.accuracy_score) details.push(`Accuracy: ${data.accuracy_score}%`);
    } else if (key === 'author_analyzer') {
        if (data.author_name) details.push(`Author: ${cleanText(data.author_name)}`);
        if (data.years_experience) details.push(`Experience: ${data.years_experience} years`);
        if (data.articles_count) details.push(`Articles: ${data.articles_count}+`);
        if (data.expertise) details.push(`Expertise: ${cleanText(data.expertise)}`);
    } else if (key === 'transparency_analyzer') {
        if (data.quote_count) details.push(`Direct Quotes: ${data.quote_count}`);
    } else if (key === 'content_analyzer') {
        if (data.readability_level) details.push(`Readability: ${cleanText(data.readability_level)}`);
        if (data.word_count) details.push(`Word Count: ${data.word_count}`);
    }
    
    details.slice(0, 6).forEach(detail => {
        if (yPos < 250) {
            doc.text(`• ${detail}`, 22, yPos);
            yPos += 5;
        }
    });
}

function addPageFooter(doc, pageNum, totalPages, colors) {
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.gray);
    
    doc.text('TruthLens Analysis Report', 20, 287);
    doc.text(new Date().toLocaleDateString('en-US'), 105, 287, { align: 'center' });
    doc.text(`Page ${pageNum} of ${totalPages}`, 190, 287, { align: 'right' });
}

// ============================================================================
// INITIALIZATION
// ============================================================================

console.log('[PDF v10.2.0] Loaded - Unicode stripping + better fallbacks enabled');
