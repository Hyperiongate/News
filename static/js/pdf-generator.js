/**
 * FILE: static/js/pdf-generator.js
 * VERSION: 3.5.0 - COMPLETE PDF FIX - MATCH WEB UI
 * DATE: October 15, 2025
 * 
 * CRITICAL FIXES FROM 3.4.0:
 * ✅ FIXED: extractAnalysisSections() now pulls REAL data (not placeholders)
 * ✅ FIXED: Text extraction handles proper data structure
 * ✅ FIXED: Content Quality "What We Found" corruption fixed
 * ✅ FIXED: Bias Detection now shows real analysis (not "Analyzed bias detector")
 * ✅ ENHANCED: Better data extraction matching web UI logic
 * ✅ PRESERVED: All mode-aware functionality (transcript vs news)
 * 
 * WEB UI PARITY: PDF now displays same rich content as web interface
 * 
 * COMPLETE FILE - NO TRUNCATION - READY TO DEPLOY
 */

// ============================================================================
// MAIN PDF GENERATION FUNCTION
// ============================================================================

function downloadPDFReport() {
    console.log('[PDF Generator v3.5.0] Starting PDF generation...');
    
    if (typeof window.jspdf === 'undefined') {
        console.error('[PDF Generator] jsPDF library not loaded');
        alert('PDF library not loaded. Please refresh the page and try again.');
        return;
    }
    
    const data = window.lastAnalysisData;
    if (!data) {
        console.error('[PDF Generator] No analysis data available');
        alert('No analysis data available. Please run an analysis first.');
        return;
    }
    
    const analysisMode = data.analysis_mode || 'news';
    console.log('[PDF Generator v3.5.0] Analysis mode:', analysisMode);
    console.log('[PDF Generator v3.5.0] Full data:', data);
    
    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        generateCompletePDFContent(doc, data);
        
        const timestamp = new Date().toISOString().split('T')[0];
        const filename = `TruthLens-${analysisMode.charAt(0).toUpperCase() + analysisMode.slice(1)}-Report-${timestamp}.pdf`;
        
        doc.save(filename);
        
        console.log('[PDF Generator v3.5.0] ✓ PDF generated successfully:', filename);
    } catch (error) {
        console.error('[PDF Generator] Error generating PDF:', error);
        console.error(error.stack);
        alert('Error generating PDF: ' + error.message);
    }
}

// ============================================================================
// PDF CONTENT GENERATION (MODE-AWARE)
// ============================================================================

function generateCompletePDFContent(doc, data) {
    const trustScore = data.trust_score || 0;
    const analysisMode = data.analysis_mode || 'news';
    const detailed = data.detailed_analysis || {};
    const insights = data.insights || {};
    
    const colors = {
        primary: [102, 126, 234],
        secondary: [118, 75, 162],
        text: [30, 41, 59],
        textLight: [100, 116, 139],
        green: [16, 185, 129],
        blue: [59, 130, 246],
        orange: [245, 158, 11],
        red: [239, 68, 68],
        purple: [139, 92, 246],
        cyan: [6, 182, 212],
        pink: [236, 72, 153]
    };
    
    generateCoverPage(doc, data, trustScore, analysisMode, colors);
    
    doc.addPage();
    generateExecutiveSummary(doc, data, insights, trustScore, colors);
    
    if (analysisMode === 'transcript') {
        if (detailed.fact_checker) {
            const service = { key: 'fact_checker', title: 'Fact Checking Analysis', color: colors.blue };
            generateCompleteServicePages(doc, service, detailed.fact_checker, colors);
        }
    } else {
        const services = [
            { key: 'source_credibility', title: 'Source Credibility Analysis', color: colors.blue },
            { key: 'bias_detector', title: 'Bias Detection Analysis', color: colors.orange },
            { key: 'fact_checker', title: 'Fact Checking Analysis', color: colors.blue },
            { key: 'author_analyzer', title: 'Author Analysis', color: colors.cyan },
            { key: 'transparency_analyzer', title: 'Transparency Analysis', color: colors.purple },
            { key: 'content_analyzer', title: 'Content Quality Analysis', color: colors.pink }
        ];
        
        services.forEach(service => {
            if (detailed[service.key]) {
                generateCompleteServicePages(doc, service, detailed[service.key], colors);
            }
        });
        
        doc.addPage();
        generateContributionPage(doc, detailed, trustScore, colors);
    }
    
    const totalPages = doc.internal.getNumberOfPages();
    for (let i = 1; i <= totalPages; i++) {
        doc.setPage(i);
        addFooter(doc, i, totalPages);
    }
}

function generateCoverPage(doc, data, trustScore, analysisMode, colors) {
    doc.setFillColor(...colors.primary);
    doc.rect(0, 0, 210, 100, 'F');
    doc.setFillColor(...colors.secondary);
    doc.rect(0, 80, 210, 20, 'F');
    
    doc.setFontSize(36);
    doc.setTextColor(255, 255, 255);
    doc.setFont('helvetica', 'bold');
    doc.text('TruthLens', 105, 40, { align: 'center' });
    
    doc.setFontSize(16);
    doc.setFont('helvetica', 'normal');
    doc.text('Complete AI-Powered Truth Analysis Report', 105, 55, { align: 'center' });
    
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    const modeText = analysisMode === 'news' ? 'NEWS ANALYSIS' : 'TRANSCRIPT ANALYSIS';
    doc.text(modeText, 105, 70, { align: 'center' });
    
    doc.setFillColor(255, 255, 255);
    doc.rect(0, 100, 210, 197, 'F');
    
    const centerX = 105;
    const centerY = 150;
    const radius = 30;
    
    let scoreColor = colors.orange;
    let scoreLabel = 'MODERATE';
    if (trustScore >= 80) {
        scoreColor = colors.green;
        scoreLabel = 'TRUSTWORTHY';
    } else if (trustScore >= 60) {
        scoreColor = colors.blue;
        scoreLabel = 'RELIABLE';
    } else if (trustScore < 40) {
        scoreColor = colors.red;
        scoreLabel = 'UNRELIABLE';
    }
    
    doc.setFillColor(245, 245, 245);
    doc.circle(centerX, centerY, radius, 'F');
    
    doc.setDrawColor(...scoreColor);
    doc.setLineWidth(3);
    doc.circle(centerX, centerY, radius, 'S');
    
    doc.setFontSize(32);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...scoreColor);
    doc.text(Math.round(trustScore).toString(), centerX, centerY - 5, { align: 'center' });
    
    doc.setFontSize(14);
    doc.setTextColor(...colors.textLight);
    doc.text('/100', centerX, centerY + 8, { align: 'center' });
    
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...scoreColor);
    doc.text(scoreLabel, centerX, centerY + 45, { align: 'center' });
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Analysis Details', 105, 210, { align: 'center' });
    
    let yPos = 225;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('Source:', 30, yPos);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    const source = data.source || 'Unknown';
    doc.text(source.substring(0, 50), 55, yPos);
    yPos += 10;
    
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('Author:', 30, yPos);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    const author = data.author || 'Unknown';
    doc.text(author.substring(0, 50), 55, yPos);
    yPos += 10;
    
    const articleTitle = data.article_summary || '';
    if (articleTitle && articleTitle.length > 5) {
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...colors.textLight);
        doc.text('Title:', 30, yPos);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        const titleLines = doc.splitTextToSize(articleTitle.substring(0, 100), 120);
        doc.text(titleLines.slice(0, 2), 55, yPos);
        yPos += 10 * Math.min(titleLines.length, 2);
    }
    
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('Generated:', 30, yPos);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    const now = new Date().toLocaleString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    doc.text(now, 55, yPos);
}

function generateExecutiveSummary(doc, data, insights, trustScore, colors) {
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.primary);
    doc.text('Executive Summary', 20, 25);
    
    doc.setDrawColor(...colors.primary);
    doc.setLineWidth(0.5);
    doc.line(20, 30, 190, 30);
    
    let yPos = 45;
    
    const articleTitle = data.article_summary || 'Analysis Summary';
    if (articleTitle && articleTitle.length > 5) {
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        doc.text('Content', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        const titleLines = doc.splitTextToSize(articleTitle, 170);
        doc.text(titleLines, 20, yPos);
        yPos += (titleLines.length * 5) + 8;
    }
    
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Source & Author', 20, yPos);
    yPos += 7;
    
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    
    const sourceInfo = [];
    if (data.source) sourceInfo.push(`Source: ${data.source}`);
    if (data.author) sourceInfo.push(`Author: ${data.author}`);
    if (data.word_count) sourceInfo.push(`Length: ${data.word_count.toLocaleString()} words`);
    
    sourceInfo.forEach(info => {
        doc.text(info, 20, yPos);
        yPos += 5;
    });
    yPos += 8;
    
    if (insights.bottom_line) {
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        doc.text('Bottom Line', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'italic');
        doc.setTextColor(...colors.blue);
        const bottomLineLines = doc.splitTextToSize(insights.bottom_line, 170);
        doc.text(bottomLineLines, 20, yPos);
        yPos += (bottomLineLines.length * 5) + 10;
        
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...colors.text);
    }
    
    const summaryText = insights.executive_summary || data.findings_summary || 'Complete comprehensive analysis conducted.';
    
    if (summaryText && summaryText.length > 10) {
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        doc.text('Analysis Findings', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        
        const summaryLines = doc.splitTextToSize(summaryText, 170);
        doc.text(summaryLines, 20, yPos);
        yPos += (summaryLines.length * 4) + 12;
    }
    
    if (insights.key_findings && Array.isArray(insights.key_findings) && insights.key_findings.length > 0) {
        if (yPos > 230) {
            doc.addPage();
            yPos = 25;
        }
        
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        doc.text('Key Findings', 20, yPos);
        yPos += 8;
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        
        insights.key_findings.forEach(finding => {
            if (yPos > 275) {
                doc.addPage();
                yPos = 25;
            }
            
            let bulletColor = colors.text;
            if (typeof finding === 'string') {
                if (finding.includes('✓')) bulletColor = colors.green;
                else if (finding.includes('⚠')) bulletColor = colors.orange;
                else if (finding.includes('✗')) bulletColor = colors.red;
            }
            
            doc.setFillColor(...bulletColor);
            doc.circle(22, yPos - 1, 1, 'F');
            
            const findingText = typeof finding === 'string' ? finding : finding.text || '';
            const findingLines = doc.splitTextToSize(findingText, 165);
            doc.text(findingLines, 26, yPos);
            yPos += (findingLines.length * 4) + 3;
        });
        
        yPos += 10;
    }
    
    if (yPos > 220) {
        doc.addPage();
        yPos = 25;
    }
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Service Scores Overview', 20, yPos);
    yPos += 8;
    
    const detailed = data.detailed_analysis || {};
    const analysisMode = data.analysis_mode || 'news';
    
    let services = [];
    
    if (analysisMode === 'transcript') {
        services = [
            { key: 'fact_checker', title: 'Fact Checking', scoreKey: 'accuracy_score' }
        ];
    } else {
        services = [
            { key: 'source_credibility', title: 'Source Credibility', scoreKey: 'credibility_score' },
            { key: 'bias_detector', title: 'Bias Detection', scoreKey: 'objectivity_score' },
            { key: 'fact_checker', title: 'Fact Checking', scoreKey: 'accuracy_score' },
            { key: 'author_analyzer', title: 'Author Analysis', scoreKey: 'credibility_score' },
            { key: 'transparency_analyzer', title: 'Transparency', scoreKey: 'transparency_score' },
            { key: 'content_analyzer', title: 'Content Quality', scoreKey: 'quality_score' }
        ];
    }
    
    doc.setFillColor(240, 240, 240);
    doc.rect(20, yPos, 170, 8, 'F');
    doc.setFontSize(9);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Service', 25, yPos + 5);
    doc.text('Score', 155, yPos + 5);
    yPos += 8;
    
    doc.setFont('helvetica', 'normal');
    services.forEach((service, index) => {
        if (detailed[service.key]) {
            const serviceData = detailed[service.key];
            const score = serviceData[service.scoreKey] || serviceData.score || 0;
            
            if (index % 2 === 0) {
                doc.setFillColor(250, 250, 250);
                doc.rect(20, yPos, 170, 7, 'F');
            }
            
            doc.setTextColor(...colors.text);
            doc.text(service.title, 25, yPos + 5);
            
            let scoreColor = colors.orange;
            if (score >= 80) scoreColor = colors.green;
            else if (score >= 60) scoreColor = colors.blue;
            else if (score < 40) scoreColor = colors.red;
            
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(...scoreColor);
            doc.text(`${Math.round(score)}/100`, 155, yPos + 5);
            doc.setFont('helvetica', 'normal');
            
            yPos += 7;
        }
    });
}

function generateCompleteServicePages(doc, service, serviceData, colors) {
    console.log(`[PDF v3.5.0] Generating ${service.title}`);
    
    doc.addPage();
    
    doc.setFillColor(...service.color);
    doc.rect(0, 0, 210, 15, 'F');
    
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text(service.title, 20, 10);
    
    let yPos = 30;
    
    let score = extractScore(service.key, serviceData);
    
    doc.setFontSize(36);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...service.color);
    doc.text(`${Math.round(score)}`, 30, yPos);
    
    doc.setFontSize(14);
    doc.setTextColor(...colors.textLight);
    doc.text('/100', 50, yPos);
    yPos += 20;
    
    if (service.key === 'source_credibility') {
        yPos = generateSourceCredibilityComplete(doc, serviceData, yPos, colors, service.color);
    } else if (service.key === 'bias_detector') {
        yPos = generateBiasDetectionComplete(doc, serviceData, yPos, colors, service.color);
    } else if (service.key === 'fact_checker') {
        yPos = generateFactCheckingComplete(doc, serviceData, yPos, colors, service.color);
    } else if (service.key === 'author_analyzer') {
        yPos = generateAuthorAnalysisComplete(doc, serviceData, yPos, colors, service.color);
    } else if (service.key === 'transparency_analyzer') {
        yPos = generateTransparencyComplete(doc, serviceData, yPos, colors, service.color);
    } else if (service.key === 'content_analyzer') {
        yPos = generateContentQualityComplete(doc, serviceData, yPos, colors, service.color);
    }
}

// ============================================================================
// FIXED: IMPROVED TEXT EXTRACTION
// ============================================================================

function extractText(value, maxLength = 500) {
    if (value === null || value === undefined) {
        return '';
    }
    
    if (typeof value === 'string') {
        return value.substring(0, maxLength);
    }
    
    if (typeof value === 'number' || typeof value === 'boolean') {
        return String(value);
    }
    
    if (Array.isArray(value)) {
        return value.map(item => extractText(item, 100)).join(', ').substring(0, maxLength);
    }
    
    if (typeof value === 'object') {
        const textFields = ['text', 'description', 'summary', 'explanation', 'analysis', 'message', 'content', 'detail', 'reason'];
        
        for (const field of textFields) {
            if (value[field] && typeof value[field] === 'string') {
                return value[field].substring(0, maxLength);
            }
        }
        
        try {
            return JSON.stringify(value).substring(0, maxLength);
        } catch {
            return String(value).substring(0, maxLength);
        }
    }
    
    return String(value).substring(0, maxLength);
}

// ============================================================================
// CRITICAL FIX: EXTRACT REAL ANALYSIS SECTIONS (NOT PLACEHOLDERS)
// ============================================================================

function extractAnalysisSections(data) {
    console.log('[PDF v3.5.0] Extracting analysis sections from:', data);
    
    const sections = {
        what_we_analyzed: '',
        what_we_found: '',
        what_it_means: ''
    };
    
    // Try direct fields first
    if (data.what_we_analyzed && typeof data.what_we_analyzed === 'string' && data.what_we_analyzed.length > 20) {
        sections.what_we_analyzed = data.what_we_analyzed;
    }
    if (data.what_we_found && typeof data.what_we_found === 'string' && data.what_we_found.length > 20) {
        sections.what_we_found = data.what_we_found;
    }
    if (data.what_it_means && typeof data.what_it_means === 'string' && data.what_it_means.length > 20) {
        sections.what_it_means = data.what_it_means;
    }
    
    // Try analysis object
    const analysisObj = data.analysis || {};
    if (!sections.what_we_analyzed && analysisObj.what_we_analyzed) {
        sections.what_we_analyzed = extractText(analysisObj.what_we_analyzed);
    }
    if (!sections.what_we_found && analysisObj.what_we_found) {
        sections.what_we_found = extractText(analysisObj.what_we_found);
    }
    if (!sections.what_it_means && analysisObj.what_it_means) {
        sections.what_it_means = extractText(analysisObj.what_it_means);
    }
    
    // Fallback to explanation/summary fields
    if (!sections.what_we_analyzed && data.explanation) {
        sections.what_we_analyzed = extractText(data.explanation);
    }
    if (!sections.what_we_found && data.findings) {
        sections.what_we_found = extractText(data.findings);
    }
    if (!sections.what_it_means && data.summary) {
        sections.what_it_means = extractText(data.summary);
    }
    
    console.log('[PDF v3.5.0] Extracted sections:', {
        analyzed: sections.what_we_analyzed.substring(0, 50) + '...',
        found: sections.what_we_found.substring(0, 50) + '...',
        means: sections.what_it_means.substring(0, 50) + '...'
    });
    
    return sections;
}

function generateSourceCredibilityComplete(doc, data, yPos, colors, serviceColor) {
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Source Information', 20, yPos);
    yPos += 8;
    
    const credScore = data.credibility_score || data.score || 0;
    
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('Credibility Score:', 20, yPos);
    yPos += 5;
    
    doc.setFillColor(240, 240, 240);
    doc.rect(20, yPos, 140, 8, 'F');
    
    const barWidth = (credScore / 100) * 140;
    let barColor = colors.orange;
    if (credScore >= 80) barColor = colors.green;
    else if (credScore >= 60) barColor = colors.blue;
    else if (credScore < 40) barColor = colors.red;
    
    doc.setFillColor(...barColor);
    doc.rect(20, yPos, barWidth, 8, 'F');
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text(`${Math.round(credScore)}/100`, 165, yPos + 6);
    yPos += 15;
    
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    
    const leftColumn = [
        ['Organization:', data.organization || data.source || 'Unknown'],
        ['Type:', data.type || 'Unknown'],
        ['Founded:', data.founded || data.established_year || 'Unknown']
    ];
    
    const rightColumn = [
        ['Reputation:', data.reputation || data.credibility_level || data.credibility || 'Unknown'],
        ['Bias:', data.bias || 'Unknown'],
        ['Awards:', data.awards || 'N/A']
    ];
    
    let startY = yPos;
    leftColumn.forEach(([label, value]) => {
        if (yPos > 270) {
            doc.addPage();
            yPos = 25;
        }
        doc.setTextColor(...colors.textLight);
        doc.text(label, 20, yPos);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        const valueLines = doc.splitTextToSize(String(value), 60);
        doc.text(valueLines, 50, yPos);
        yPos += Math.max(5, valueLines.length * 5);
        doc.setFont('helvetica', 'normal');
    });
    
    let rightYPos = startY;
    rightColumn.forEach(([label, value]) => {
        doc.setTextColor(...colors.textLight);
        doc.text(label, 110, rightYPos);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        const valueLines = doc.splitTextToSize(String(value), 60);
        doc.text(valueLines, 140, rightYPos);
        rightYPos += Math.max(5, valueLines.length * 5);
        doc.setFont('helvetica', 'normal');
    });
    
    yPos = Math.max(yPos, rightYPos) + 8;
    
    const analysisSections = extractAnalysisSections(data);
    const sectionTitles = [
        { title: 'What We Analyzed', key: 'what_we_analyzed' },
        { title: 'What We Found', key: 'what_we_found' },
        { title: 'What It Means', key: 'what_it_means' }
    ];
    
    sectionTitles.forEach(section => {
        const text = analysisSections[section.key];
        
        if (text && text.length > 10) {
            if (yPos > 250) {
                doc.addPage();
                yPos = 25;
            }
            
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(...colors.text);
            doc.text(section.title, 20, yPos);
            yPos += 7;
            
            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            const textLines = doc.splitTextToSize(text, 170);
            doc.text(textLines, 20, yPos);
            yPos += (textLines.length * 4) + 8;
        }
    });
    
    return yPos;
}

function generateBiasDetectionComplete(doc, data, yPos, colors, serviceColor) {
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Bias Analysis Summary', 20, yPos);
    yPos += 8;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text('Political Spectrum', 20, yPos);
    yPos += 6;
    
    const spectrumWidth = 150;
    const spectrumX = 30;
    
    const sections = [
        { color: [220, 38, 38], width: 30 },
        { color: [239, 68, 68], width: 30 },
        { color: [156, 163, 175], width: 30 },
        { color: [59, 130, 246], width: 30 },
        { color: [29, 78, 216], width: 30 }
    ];
    
    let sectionX = spectrumX;
    sections.forEach(section => {
        doc.setFillColor(...section.color);
        doc.rect(sectionX, yPos, section.width, 8, 'F');
        sectionX += section.width;
    });
    
    const politicalLabel = data.political_label || data.political_leaning || data.direction || 'Center';
    let indicatorX = spectrumX + (spectrumWidth / 2);
    
    if (politicalLabel.toLowerCase().includes('left')) {
        indicatorX = spectrumX + (spectrumWidth * 0.25);
        if (politicalLabel.toLowerCase().includes('far')) indicatorX = spectrumX + 15;
    } else if (politicalLabel.toLowerCase().includes('right')) {
        indicatorX = spectrumX + (spectrumWidth * 0.75);
        if (politicalLabel.toLowerCase().includes('far')) indicatorX = spectrumX + spectrumWidth - 15;
    }
    
    const triangleColor = [0, 0, 0];
    drawTriangle(doc, indicatorX - 3, yPos - 2, indicatorX + 3, yPos - 2, indicatorX, yPos + 1, triangleColor);
    drawTriangle(doc, indicatorX - 3, yPos + 9, indicatorX + 3, yPos + 9, indicatorX, yPos + 7, triangleColor);
    
    doc.setFontSize(7);
    doc.setTextColor(...colors.textLight);
    doc.text('Far Left', spectrumX, yPos + 13);
    doc.text('Center', spectrumX + (spectrumWidth / 2), yPos + 13, { align: 'center' });
    doc.text('Far Right', spectrumX + spectrumWidth, yPos + 13, { align: 'right' });
    
    yPos += 20;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text(`Position: ${politicalLabel}`, 20, yPos);
    yPos += 10;
    
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    
    const metrics = [
        ['Objectivity Score', `${Math.round(data.objectivity_score || 0)}/100`],
        ['Sensationalism', data.sensationalism_level || 'Low'],
        ['Bias Rating', data.bias_rating || data.bias_level || 'Minimal']
    ];
    
    metrics.forEach(([label, value]) => {
        doc.setTextColor(...colors.textLight);
        doc.text(label + ':', 25, yPos);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        doc.text(String(value), 80, yPos);
        yPos += 6;
        doc.setFont('helvetica', 'normal');
    });
    
    yPos += 5;
    
    const analysisSections = extractAnalysisSections(data);
    const sectionTitles = [
        { title: 'What We Analyzed', key: 'what_we_analyzed' },
        { title: 'What We Found', key: 'what_we_found' },
        { title: 'What It Means', key: 'what_it_means' }
    ];
    
    sectionTitles.forEach(section => {
        const text = analysisSections[section.key];
        
        if (text && text.length > 10) {
            if (yPos > 250) {
                doc.addPage();
                yPos = 25;
            }
            
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text(section.title, 20, yPos);
            yPos += 7;
            
            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            const textLines = doc.splitTextToSize(text, 170);
            doc.text(textLines, 20, yPos);
            yPos += (textLines.length * 4) + 8;
        }
    });
    
    return yPos;
}

function generateFactCheckingComplete(doc, data, yPos, colors, serviceColor) {
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Fact Check Summary', 20, yPos);
    yPos += 8;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    
    const claimsChecked = data.claims_checked || data.claims_found || data.total_claims || 0;
    const claimsVerified = data.claims_verified || data.verified_count || 0;
    const accuracyScore = data.accuracy_score || data.verification_score || data.score || 0;
    
    const fields = [
        ['Claims Analyzed', claimsChecked],
        ['Claims Verified', claimsVerified],
        ['Accuracy Score', `${Math.round(accuracyScore)}%`],
        ['Verification Rate', `${Math.round((claimsVerified / Math.max(claimsChecked, 1)) * 100)}%`]
    ];
    
    fields.forEach(([label, value]) => {
        doc.setTextColor(...colors.textLight);
        doc.text(label + ':', 25, yPos);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        doc.text(String(value), 80, yPos);
        yPos += 6;
        doc.setFont('helvetica', 'normal');
    });
    
    yPos += 8;
    
    const analysisSections = extractAnalysisSections(data);
    const sectionTitles = [
        { title: 'What We Analyzed', key: 'what_we_analyzed' },
        { title: 'What We Found', key: 'what_we_found' },
        { title: 'What It Means', key: 'what_it_means' }
    ];
    
    sectionTitles.forEach(section => {
        const text = analysisSections[section.key];
        
        if (text && text.length > 10) {
            if (yPos > 250) {
                doc.addPage();
                yPos = 25;
            }
            
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text(section.title, 20, yPos);
            yPos += 7;
            
            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            const textLines = doc.splitTextToSize(text, 170);
            doc.text(textLines, 20, yPos);
            yPos += (textLines.length * 4) + 8;
        }
    });
    
    const claims = data.fact_checks || data.claims || data.claims_analyzed || [];
    
    if (claims.length > 0) {
        if (yPos > 250) {
            doc.addPage();
            yPos = 25;
        }
        
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.text('All Claims Checked', 20, yPos);
        yPos += 7;
        
        claims.forEach((claim, idx) => {
            if (yPos > 260) {
                doc.addPage();
                yPos = 25;
            }
            
            doc.setFontSize(10);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(...colors.text);
            doc.text(`Claim ${idx + 1}:`, 20, yPos);
            
            const verdict = claim.verdict || claim.status || 'unverified';
            const verdictColor = getVerdictColor(verdict, colors);
            doc.setTextColor(...verdictColor);
            doc.text(verdict.toUpperCase().replace('_', ' '), 160, yPos);
            yPos += 6;
            
            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            doc.setTextColor(...colors.text);
            const claimText = extractText(claim.claim || claim.text || claim.statement || claim, 300);
            const claimLines = doc.splitTextToSize(claimText, 170);
            doc.text(claimLines, 20, yPos);
            yPos += (claimLines.length * 4) + 3;
            
            const explanation = extractText(claim.explanation || claim.analysis || claim.reason, 300);
            if (explanation) {
                doc.setFont('helvetica', 'italic');
                doc.setTextColor(...colors.textLight);
                doc.setFontSize(8);
                const explLines = doc.splitTextToSize(explanation, 170);
                doc.text(explLines, 20, yPos);
                yPos += (explLines.length * 3.5) + 2;
            }
            
            if (claim.confidence) {
                doc.setFontSize(8);
                doc.setFont('helvetica', 'normal');
                doc.setTextColor(...colors.textLight);
                doc.text(`Confidence: ${claim.confidence}%`, 20, yPos);
                yPos += 4;
            }
            
            yPos += 5;
        });
    }
    
    return yPos;
}

function generateAuthorAnalysisComplete(doc, data, yPos, colors, serviceColor) {
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Author Profile', 20, yPos);
    yPos += 8;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    
    const fields = [
        ['Name', data.name || data.primary_author || data.author_name || 'Unknown'],
        ['Position', data.position || data.role || 'Journalist'],
        ['Organization', data.organization || data.domain || 'Unknown'],
        ['Credibility Score', `${Math.round(data.credibility_score || data.score || 0)}/100`],
        ['Expertise Level', extractText(data.expertise_level || data.expertise || 'Unknown')],
        ['Years Experience', data.years_experience || data.experience || 'Unknown'],
        ['Verified', data.verified ? 'Yes' : 'No']
    ];
    
    fields.forEach(([label, value]) => {
        if (yPos > 270) {
            doc.addPage();
            yPos = 25;
        }
        
        doc.setTextColor(...colors.textLight);
        doc.text(label + ':', 25, yPos);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        const valueLines = doc.splitTextToSize(String(value), 140);
        doc.text(valueLines, 70, yPos);
        yPos += Math.max(6, valueLines.length * 5);
        doc.setFont('helvetica', 'normal');
    });
    
    yPos += 5;
    
    const analysisSections = extractAnalysisSections(data);
    const sectionTitles = [
        { title: 'What We Analyzed', key: 'what_we_analyzed' },
        { title: 'What We Found', key: 'what_we_found' },
        { title: 'What It Means', key: 'what_it_means' }
    ];
    
    sectionTitles.forEach(section => {
        const text = analysisSections[section.key];
        
        if (text && text.length > 10) {
            if (yPos > 250) {
                doc.addPage();
                yPos = 25;
            }
            
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text(section.title, 20, yPos);
            yPos += 7;
            
            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            const textLines = doc.splitTextToSize(text, 170);
            doc.text(textLines, 20, yPos);
            yPos += (textLines.length * 4) + 8;
        }
    });
    
    return yPos;
}

function generateTransparencyComplete(doc, data, yPos, colors, serviceColor) {
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Transparency Assessment', 20, yPos);
    yPos += 8;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    
    const fields = [
        ['Transparency Level', data.transparency_level || data.level || 'Unknown'],
        ['Transparency Score', `${Math.round(data.transparency_score || data.score || 0)}/100`],
        ['Article Type', data.article_type || data.content_type || 'News Report'],
        ['Sources Cited', data.sources_count || data.source_count || data.sources_cited || 'Unknown'],
        ['Direct Quotes', data.quotes_count || data.quote_count || data.quotes_used || 'Unknown']
    ];
    
    fields.forEach(([label, value]) => {
        doc.setTextColor(...colors.textLight);
        doc.text(label + ':', 25, yPos);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        doc.text(String(value), 80, yPos);
        yPos += 6;
        doc.setFont('helvetica', 'normal');
    });
    
    yPos += 8;
    
    const analysisSections = extractAnalysisSections(data);
    const sectionTitles = [
        { title: 'What We Analyzed', key: 'what_we_analyzed' },
        { title: 'What We Found', key: 'what_we_found' },
        { title: 'What It Means', key: 'what_it_means' }
    ];
    
    sectionTitles.forEach(section => {
        const text = analysisSections[section.key];
        
        if (text && text.length > 10) {
            if (yPos > 250) {
                doc.addPage();
                yPos = 25;
            }
            
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text(section.title, 20, yPos);
            yPos += 7;
            
            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            const textLines = doc.splitTextToSize(text, 170);
            doc.text(textLines, 20, yPos);
            yPos += (textLines.length * 4) + 8;
        }
    });
    
    return yPos;
}

function generateContentQualityComplete(doc, data, yPos, colors, serviceColor) {
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Content Quality Metrics', 20, yPos);
    yPos += 8;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    
    const fields = [
        ['Quality Score', `${Math.round(data.quality_score || data.score || 0)}/100`],
        ['Readability Level', data.readability_level || data.readability || 'Unknown'],
        ['Word Count', (data.word_count || 0).toLocaleString()],
        ['Sentence Count', data.sentence_count || 'Unknown'],
        ['Average Sentence Length', data.avg_sentence_length ? `${Math.round(data.avg_sentence_length)} words` : 'Unknown'],
        ['Paragraph Count', data.paragraph_count || 'Unknown'],
        ['Grammar Issues', data.grammar_issues || data.grammar_errors || 'None detected']
    ];
    
    fields.forEach(([label, value]) => {
        if (yPos > 270) {
            doc.addPage();
            yPos = 25;
        }
        
        doc.setTextColor(...colors.textLight);
        doc.text(label + ':', 25, yPos);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        const valueLines = doc.splitTextToSize(String(value), 140);
        doc.text(valueLines, 80, yPos);
        yPos += Math.max(6, valueLines.length * 5);
        doc.setFont('helvetica', 'normal');
    });
    
    yPos += 5;
    
    const analysisSections = extractAnalysisSections(data);
    const sectionTitles = [
        { title: 'What We Analyzed', key: 'what_we_analyzed' },
        { title: 'What We Found', key: 'what_we_found' },
        { title: 'What It Means', key: 'what_it_means' }
    ];
    
    sectionTitles.forEach(section => {
        const text = analysisSections[section.key];
        
        if (text && text.length > 10) {
            if (yPos > 250) {
                doc.addPage();
                yPos = 25;
            }
            
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text(section.title, 20, yPos);
            yPos += 7;
            
            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            const textLines = doc.splitTextToSize(text, 170);
            doc.text(textLines, 20, yPos);
            yPos += (textLines.length * 4) + 8;
        }
    });
    
    return yPos;
}

function generateContributionPage(doc, detailed, trustScore, colors) {
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.primary);
    doc.text('Score Contribution Breakdown', 20, 25);
    
    doc.setDrawColor(...colors.primary);
    doc.setLineWidth(0.5);
    doc.line(20, 30, 190, 30);
    
    let yPos = 45;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.text);
    const explanation = 'Each service contributes to the overall trust score based on its weighted importance. Below is the breakdown showing how each service contributed to the final score.';
    const explLines = doc.splitTextToSize(explanation, 170);
    doc.text(explLines, 20, yPos);
    yPos += (explLines.length * 5) + 15;
    
    const services = [
        { key: 'source_credibility', title: 'Source Credibility', weight: 0.25, color: colors.blue },
        { key: 'bias_detector', title: 'Bias Detection', weight: 0.20, color: colors.orange },
        { key: 'author_analyzer', title: 'Author Analysis', weight: 0.15, color: colors.cyan },
        { key: 'fact_checker', title: 'Fact Checking', weight: 0.15, color: colors.blue },
        { key: 'transparency_analyzer', title: 'Transparency', weight: 0.10, color: colors.purple },
        { key: 'content_analyzer', title: 'Content Quality', weight: 0.05, color: colors.pink }
    ];
    
    services.forEach(service => {
        if (detailed[service.key]) {
            const serviceData = detailed[service.key];
            const score = extractScore(service.key, serviceData);
            const contribution = (score * service.weight).toFixed(1);
            const maxContribution = service.weight * 100;
            
            doc.setFontSize(10);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(...colors.text);
            doc.text(service.title, 20, yPos);
            
            doc.setFont('helvetica', 'normal');
            doc.setTextColor(...colors.textLight);
            doc.text(`${Math.round(service.weight * 100)}%`, 180, yPos);
            yPos += 5;
            
            doc.setFillColor(240, 240, 240);
            doc.rect(20, yPos, 160, 6, 'F');
            
            const barWidth = (score / 100) * 160;
            doc.setFillColor(...service.color);
            doc.rect(20, yPos, barWidth, 6, 'F');
            
            doc.setFontSize(8);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(255, 255, 255);
            if (barWidth > 20) {
                doc.text(`${contribution}/${maxContribution}`, 22, yPos + 4);
            }
            
            yPos += 12;
            
            if (yPos > 260) {
                doc.addPage();
                yPos = 25;
            }
        }
    });
    
    yPos += 10;
    doc.setDrawColor(...colors.primary);
    doc.setLineWidth(0.5);
    doc.line(20, yPos, 190, yPos);
    yPos += 10;
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Final Trust Score', 20, yPos);
    
    doc.setFontSize(24);
    doc.setTextColor(...colors.primary);
    doc.text(`${Math.round(trustScore)}/100`, 155, yPos);
}

function addFooter(doc, pageNum, totalPages) {
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(150, 150, 150);
    
    doc.text(`Page ${pageNum} of ${totalPages}`, 105, 290, { align: 'center' });
    doc.text('Generated by TruthLens - AI-Powered Truth Analysis', 105, 285, { align: 'center' });
}

function extractScore(serviceKey, serviceData) {
    if (serviceKey === 'source_credibility') {
        return serviceData.credibility_score || serviceData.score || 0;
    } else if (serviceKey === 'bias_detector') {
        return serviceData.objectivity_score || serviceData.score || 0;
    } else if (serviceKey === 'fact_checker') {
        return serviceData.verification_score || serviceData.accuracy_score || serviceData.score || 0;
    } else if (serviceKey === 'author_analyzer') {
        return serviceData.credibility_score || serviceData.score || 0;
    } else if (serviceKey === 'transparency_analyzer') {
        return serviceData.transparency_score || serviceData.score || 0;
    } else if (serviceKey === 'content_analyzer') {
        return serviceData.quality_score || serviceData.score || 0;
    }
    return 0;
}

function getVerdictColor(verdict, colors) {
    const v = verdict.toLowerCase();
    
    if (v === 'true' || v === 'mostly_true' || v === 'nearly_true') return colors.green;
    if (v === 'false' || v === 'mostly_false') return colors.red;
    if (v === 'exaggeration' || v === 'misleading' || v === 'needs_context') return colors.orange;
    if (v === 'empty_rhetoric' || v === 'opinion') return colors.textLight;
    if (v === 'unsubstantiated_prediction') return colors.purple;
    
    return colors.orange;
}

function drawTriangle(doc, x1, y1, x2, y2, x3, y3, fillColor) {
    doc.setFillColor(...fillColor);
    doc.lines([[x2 - x1, y2 - y1], [x3 - x2, y3 - y2], [x1 - x3, y1 - y3]], x1, y1, null, 'F');
}

console.log('[PDF Generator v3.5.0] Loaded - COMPLETE FIX - WEB UI PARITY');
