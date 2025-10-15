/**
 * FILE: static/js/pdf-generator.js
 * VERSION: 3.3.0 - EXECUTIVE SUMMARY FIX + REAL DATA
 * DATE: October 14, 2025
 * 
 * CRITICAL FIXES FROM 3.2.1:
 * ✅ FIXED: Executive Summary now shows REAL content instead of placeholders
 * ✅ FIXED: Pulls from insights.executive_summary and findings_summary
 * ✅ FIXED: Shows article title, source, author, word count
 * ✅ FIXED: Displays key_findings bullets
 * ✅ FIXED: Source credibility uses real data (not "Analyzed source credibility")
 * ✅ ADDED: Better handling of missing article object
 * 
 * FROM 3.2.1:
 * ✅ REMOVED: Unreliable hook system
 * ✅ SIMPLIFIED: Direct access to window.lastAnalysisData
 * 
 * FROM 3.2.0:
 * ✅ ENHANCED: All visual charts and graphics
 * ✅ COMPLETE: All 6 service analysis pages with full details
 */

// ============================================================================
// MAIN PDF GENERATION FUNCTION
// ============================================================================

function downloadPDFReport() {
    console.log('[PDF Generator v3.3.0] Starting comprehensive PDF generation...');
    
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
    
    console.log('[PDF Generator] Full data structure:', data);
    
    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        generateCompletePDFContent(doc, data);
        
        const timestamp = new Date().toISOString().split('T')[0];
        const mode = data.analysis_mode || 'news';
        const filename = `TruthLens-Complete-${mode.charAt(0).toUpperCase() + mode.slice(1)}-Report-${timestamp}.pdf`;
        
        doc.save(filename);
        
        console.log('[PDF Generator] ✓ Complete PDF generated successfully:', filename);
    } catch (error) {
        console.error('[PDF Generator] Error generating PDF:', error);
        console.error(error.stack);
        alert('Error generating PDF: ' + error.message);
    }
}

// ============================================================================
// PDF CONTENT GENERATION
// ============================================================================

function generateCompletePDFContent(doc, data) {
    const trustScore = data.trust_score || 0;
    const analysisMode = data.analysis_mode || 'news';
    const detailed = data.detailed_analysis || {};
    const insights = data.insights || {};
    
    console.log('[PDF] Detailed analysis:', detailed);
    console.log('[PDF] Insights:', insights);
    
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
        pink: [236, 72, 153],
        amber: [217, 119, 6]
    };
    
    // Page 1: Cover Page
    generateCoverPage(doc, data, trustScore, analysisMode, colors);
    
    // Page 2: Executive Summary (NOW WITH REAL CONTENT!)
    doc.addPage();
    generateExecutiveSummary(doc, data, insights, trustScore, colors);
    
    // Service Pages - COMPREHENSIVE with all details
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
    
    // Final Page: Contribution Breakdown
    doc.addPage();
    generateContributionPage(doc, detailed, trustScore, colors);
    
    // Add footer to all pages
    const totalPages = doc.internal.getNumberOfPages();
    for (let i = 1; i <= totalPages; i++) {
        doc.setPage(i);
        addFooter(doc, i, totalPages);
    }
}

// ============================================================================
// COVER PAGE
// ============================================================================

function generateCoverPage(doc, data, trustScore, analysisMode, colors) {
    // Purple gradient background (simulated with rectangles)
    doc.setFillColor(...colors.primary);
    doc.rect(0, 0, 210, 100, 'F');
    doc.setFillColor(...colors.secondary);
    doc.rect(0, 80, 210, 20, 'F');
    
    // TruthLens Logo
    doc.setFontSize(36);
    doc.setTextColor(255, 255, 255);
    doc.setFont('helvetica', 'bold');
    doc.text('TruthLens', 105, 40, { align: 'center' });
    
    // Subtitle
    doc.setFontSize(16);
    doc.setFont('helvetica', 'normal');
    doc.text('Complete AI-Powered Truth Analysis Report', 105, 55, { align: 'center' });
    
    // Analysis Type
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    const modeText = analysisMode === 'news' ? 'NEWS ANALYSIS' : 'TRANSCRIPT ANALYSIS';
    doc.text(modeText, 105, 70, { align: 'center' });
    
    // White section
    doc.setFillColor(255, 255, 255);
    doc.rect(0, 100, 210, 197, 'F');
    
    // Trust Score Circle
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
    
    // Circle background
    doc.setFillColor(245, 245, 245);
    doc.circle(centerX, centerY, radius, 'F');
    
    // Circle border
    doc.setDrawColor(...scoreColor);
    doc.setLineWidth(3);
    doc.circle(centerX, centerY, radius, 'S');
    
    // Score number
    doc.setFontSize(32);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...scoreColor);
    doc.text(Math.round(trustScore).toString(), centerX, centerY - 5, { align: 'center' });
    
    // "/100" text
    doc.setFontSize(14);
    doc.setTextColor(...colors.textLight);
    doc.text('/100', centerX, centerY + 8, { align: 'center' });
    
    // Score label
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...scoreColor);
    doc.text(scoreLabel, centerX, centerY + 45, { align: 'center' });
    
    // Article Info
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Analysis Details', 105, 210, { align: 'center' });
    
    let yPos = 225;
    
    // Source
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('Source:', 30, yPos);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    const source = data.source || 'Unknown';
    doc.text(source.substring(0, 50), 55, yPos);
    yPos += 10;
    
    // Author
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('Author:', 30, yPos);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    const author = data.author || 'Unknown';
    doc.text(author.substring(0, 50), 55, yPos);
    yPos += 10;
    
    // Title (if available)
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
    
    // Date
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

// ============================================================================
// EXECUTIVE SUMMARY PAGE (COMPLETELY REWRITTEN FOR v3.3.0)
// ============================================================================

function generateExecutiveSummary(doc, data, insights, trustScore, colors) {
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.primary);
    doc.text('Executive Summary', 20, 25);
    
    doc.setDrawColor(...colors.primary);
    doc.setLineWidth(0.5);
    doc.line(20, 30, 190, 30);
    
    let yPos = 45;
    
    // Article Title
    const articleTitle = data.article_summary || 'Article Analysis';
    if (articleTitle && articleTitle.length > 5) {
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        doc.text('Article', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        const titleLines = doc.splitTextToSize(articleTitle, 170);
        doc.text(titleLines, 20, yPos);
        yPos += (titleLines.length * 5) + 8;
    }
    
    // Source & Author Information
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
    
    // Bottom Line (if available from insights)
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
    
    // Analysis Findings (use insights.executive_summary or findings_summary)
    const summaryText = insights.executive_summary || data.findings_summary || 'Complete comprehensive analysis conducted across all services.';
    
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
    
    // Key Findings Bullets (from insights.key_findings)
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
            
            // Determine color based on finding symbol
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
    
    // Service Scores Table
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
    const services = [
        { key: 'source_credibility', title: 'Source Credibility', scoreKey: 'credibility_score' },
        { key: 'bias_detector', title: 'Bias Detection', scoreKey: 'objectivity_score' },
        { key: 'fact_checker', title: 'Fact Checking', scoreKey: 'accuracy_score' },
        { key: 'author_analyzer', title: 'Author Analysis', scoreKey: 'credibility_score' },
        { key: 'transparency_analyzer', title: 'Transparency', scoreKey: 'transparency_score' },
        { key: 'content_analyzer', title: 'Content Quality', scoreKey: 'quality_score' }
    ];
    
    // Table header
    doc.setFillColor(240, 240, 240);
    doc.rect(20, yPos, 170, 8, 'F');
    doc.setFontSize(9);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Service', 25, yPos + 5);
    doc.text('Score', 155, yPos + 5);
    yPos += 8;
    
    // Table rows
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

// ============================================================================
// SERVICE PAGES - COMPLETE WITH ALL DETAILS
// ============================================================================

function generateCompleteServicePages(doc, service, serviceData, colors) {
    console.log(`[PDF] Generating COMPLETE ${service.title} with data:`, serviceData);
    
    // Start new page
    doc.addPage();
    
    // Service header
    doc.setFillColor(...service.color);
    doc.rect(0, 0, 210, 15, 'F');
    
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text(service.title, 20, 10);
    
    let yPos = 30;
    
    // Extract score
    let score = extractScore(service.key, serviceData);
    
    // Score badge
    doc.setFontSize(36);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...service.color);
    doc.text(`${Math.round(score)}`, 30, yPos);
    
    doc.setFontSize(14);
    doc.setTextColor(...colors.textLight);
    doc.text('/100', 50, yPos);
    yPos += 20;
    
    // Generate service-specific complete content
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
// TEXT EXTRACTION HELPER
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

function extractAnalysisSections(data) {
    const sections = {
        what_we_analyzed: '',
        what_we_found: '',
        what_it_means: ''
    };
    
    // Try to get from nested 'analysis' object first
    const analysisObj = data.analysis || {};
    
    // Map different field names to our standard sections
    const fieldMappings = {
        what_we_analyzed: ['what_we_looked', 'what_analyzed', 'analyzed', 'methodology'],
        what_we_found: ['what_we_found', 'what_found', 'found', 'findings_text', 'findings'],
        what_it_means: ['what_it_means', 'what_means', 'means', 'interpretation', 'significance', 'summary']
    };
    
    // Try to extract from analysis object
    for (const [section, possibleFields] of Object.entries(fieldMappings)) {
        for (const field of possibleFields) {
            if (analysisObj[field] && typeof analysisObj[field] === 'string' && analysisObj[field].length > 10) {
                // Skip placeholder text
                if (!analysisObj[field].includes('Analyzed source') && 
                    !analysisObj[field].includes('Analysis completed') && 
                    !analysisObj[field].includes('Results processed')) {
                    sections[section] = extractText(analysisObj[field]);
                    break;
                }
            }
        }
        
        // If not found in analysis object, try top level
        if (!sections[section]) {
            for (const field of possibleFields) {
                if (data[field] && typeof data[field] === 'string' && data[field].length > 10) {
                    if (!data[field].includes('Analyzed source') && 
                        !data[field].includes('Analysis completed') && 
                        !data[field].includes('Results processed')) {
                        sections[section] = extractText(data[field]);
                        break;
                    }
                }
            }
        }
    }
    
    return sections;
}

// ============================================================================
// SOURCE CREDIBILITY ANALYSIS (FIXED FOR v3.3.0)
// ============================================================================

function generateSourceCredibilityComplete(doc, data, yPos, colors, serviceColor) {
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Source Information', 20, yPos);
    yPos += 8;
    
    // Create a visual credibility meter
    const credScore = data.credibility_score || data.score || 0;
    
    // Draw credibility bar
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('Credibility Score:', 20, yPos);
    yPos += 5;
    
    // Bar background
    doc.setFillColor(240, 240, 240);
    doc.rect(20, yPos, 140, 8, 'F');
    
    // Bar fill
    const barWidth = (credScore / 100) * 140;
    let barColor = colors.orange;
    if (credScore >= 80) barColor = colors.green;
    else if (credScore >= 60) barColor = colors.blue;
    else if (credScore < 40) barColor = colors.red;
    
    doc.setFillColor(...barColor);
    doc.rect(20, yPos, barWidth, 8, 'F');
    
    // Score text
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text(`${Math.round(credScore)}/100`, 165, yPos + 6);
    yPos += 15;
    
    // Detailed fields in two columns
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
    
    // Left column
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
    
    // Right column (reset yPos)
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
    
    // Reputation indicator graphic
    const reputation = (data.reputation || data.credibility_level || data.credibility || '').toLowerCase();
    if (reputation && reputation !== 'unknown') {
        doc.setFontSize(10);
        doc.setFont('helvetica', 'bold');
        doc.text('Reputation Assessment', 20, yPos);
        yPos += 6;
        
        // Visual reputation indicator
        const repLevels = [
            { label: 'Very Low', active: reputation.includes('very low') || reputation.includes('poor') },
            { label: 'Low', active: reputation === 'low' },
            { label: 'Medium', active: reputation === 'medium' || reputation === 'moderate' },
            { label: 'High', active: reputation === 'high' },
            { label: 'Excellent', active: reputation.includes('excellent') || reputation.includes('very high') }
        ];
        
        let xPos = 20;
        repLevels.forEach((level, idx) => {
            const boxColor = level.active ? colors.green : [220, 220, 220];
            doc.setFillColor(...boxColor);
            doc.rect(xPos, yPos, 30, 6, 'F');
            
            doc.setFontSize(7);
            doc.setTextColor(level.active ? 255 : 150, level.active ? 255 : 150, level.active ? 255 : 150);
            doc.text(level.label, xPos + 15, yPos + 4, { align: 'center' });
            
            xPos += 32;
        });
        yPos += 12;
    }
    
    yPos += 5;
    
    // Analysis sections - USE REAL DATA
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

// ============================================================================
// BIAS DETECTION ANALYSIS
// ============================================================================

function generateBiasDetectionComplete(doc, data, yPos, colors, serviceColor) {
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Bias Analysis Summary', 20, yPos);
    yPos += 8;
    
    // Political Spectrum Graphic
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text('Political Spectrum', 20, yPos);
    yPos += 6;
    
    // Draw political spectrum bar
    const spectrumWidth = 150;
    const spectrumX = 30;
    
    // Background spectrum (gradient simulation with sections)
    const sections = [
        { color: [220, 38, 38], width: 30 },   // Far left - red
        { color: [239, 68, 68], width: 30 },   // Left - lighter red
        { color: [156, 163, 175], width: 30 }, // Center - gray
        { color: [59, 130, 246], width: 30 },  // Right - blue
        { color: [29, 78, 216], width: 30 }    // Far right - dark blue
    ];
    
    let sectionX = spectrumX;
    sections.forEach(section => {
        doc.setFillColor(...section.color);
        doc.rect(sectionX, yPos, section.width, 8, 'F');
        sectionX += section.width;
    });
    
    // Political position indicator
    const politicalLabel = data.political_label || data.political_leaning || data.direction || 'Center';
    let indicatorX = spectrumX + (spectrumWidth / 2); // Default center
    
    if (politicalLabel.toLowerCase().includes('left')) {
        indicatorX = spectrumX + (spectrumWidth * 0.25);
        if (politicalLabel.toLowerCase().includes('far')) indicatorX = spectrumX + 15;
    } else if (politicalLabel.toLowerCase().includes('right')) {
        indicatorX = spectrumX + (spectrumWidth * 0.75);
        if (politicalLabel.toLowerCase().includes('far')) indicatorX = spectrumX + spectrumWidth - 15;
    }
    
    // Draw indicator triangle (pointing down and up)
    const triangleColor = [0, 0, 0];
    // Top triangle (pointing down)
    drawTriangle(doc, indicatorX - 3, yPos - 2, indicatorX + 3, yPos - 2, indicatorX, yPos + 1, triangleColor);
    // Bottom triangle (pointing up)
    drawTriangle(doc, indicatorX - 3, yPos + 9, indicatorX + 3, yPos + 9, indicatorX, yPos + 7, triangleColor);
    
    // Labels
    doc.setFontSize(7);
    doc.setTextColor(...colors.textLight);
    doc.text('Far Left', spectrumX, yPos + 13);
    doc.text('Center', spectrumX + (spectrumWidth / 2), yPos + 13, { align: 'center' });
    doc.text('Far Right', spectrumX + spectrumWidth, yPos + 13, { align: 'right' });
    
    yPos += 20;
    
    // Political position label
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text(`Position: ${politicalLabel}`, 20, yPos);
    yPos += 10;
    
    // Metrics in grid format
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
    
    // Bias indicators visual
    const biasScore = data.objectivity_score || 0;
    if (biasScore > 0) {
        doc.setFontSize(10);
        doc.setFont('helvetica', 'bold');
        doc.text('Objectivity Assessment', 20, yPos);
        yPos += 6;
        
        // Progress bar
        doc.setFillColor(240, 240, 240);
        doc.rect(20, yPos, 140, 8, 'F');
        
        const objBarWidth = (biasScore / 100) * 140;
        let objColor = colors.orange;
        if (biasScore >= 80) objColor = colors.green;
        else if (biasScore >= 60) objColor = colors.blue;
        
        doc.setFillColor(...objColor);
        doc.rect(20, yPos, objBarWidth, 8, 'F');
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        doc.text(`${Math.round(biasScore)}%`, 165, yPos + 6);
        
        yPos += 15;
    }
    
    // What we analyzed/found/means sections
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
    
    // Loaded Language Examples
    const details = data.details || {};
    const loadedLanguage = details.loaded_language_examples || data.loaded_language_examples || data.loaded_phrases || [];
    
    if (loadedLanguage.length > 0) {
        if (yPos > 250) {
            doc.addPage();
            yPos = 25;
        }
        
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text('Loaded Language Examples', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        
        loadedLanguage.slice(0, 10).forEach((example, idx) => {
            if (yPos > 275) {
                doc.addPage();
                yPos = 25;
            }
            
            const exampleText = extractText(example, 200);
            
            doc.setFillColor(...serviceColor);
            doc.circle(22, yPos - 1, 0.8, 'F');
            
            const exLines = doc.splitTextToSize(exampleText, 165);
            doc.text(exLines, 26, yPos);
            yPos += (exLines.length * 4) + 2;
        });
        
        yPos += 5;
    }
    
    return yPos;
}

// ============================================================================
// FACT CHECKING ANALYSIS
// ============================================================================

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
    
    // What we analyzed/found/means sections
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
    
    // COMPLETE CLAIMS LIST - ALL CLAIMS WITH VERDICTS
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
            
            // Claim number and verdict
            doc.setFontSize(10);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(...colors.text);
            doc.text(`Claim ${idx + 1}:`, 20, yPos);
            
            const verdict = claim.verdict || claim.status || 'unverified';
            const verdictColor = getVerdictColor(verdict, colors);
            doc.setTextColor(...verdictColor);
            doc.text(verdict.toUpperCase(), 160, yPos);
            yPos += 6;
            
            // Claim text
            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            doc.setTextColor(...colors.text);
            const claimText = extractText(claim.claim || claim.text || claim.statement || claim, 300);
            const claimLines = doc.splitTextToSize(claimText, 170);
            doc.text(claimLines, 20, yPos);
            yPos += (claimLines.length * 4) + 3;
            
            // Explanation/Analysis
            const explanation = extractText(claim.explanation || claim.analysis || claim.reason, 300);
            if (explanation) {
                doc.setFont('helvetica', 'italic');
                doc.setTextColor(...colors.textLight);
                doc.setFontSize(8);
                const explLines = doc.splitTextToSize(explanation, 170);
                doc.text(explLines, 20, yPos);
                yPos += (explLines.length * 3.5) + 2;
            }
            
            // Confidence score if available
            if (claim.confidence) {
                doc.setFontSize(8);
                doc.setFont('helvetica', 'normal');
                doc.setTextColor(...colors.textLight);
                doc.text(`Confidence: ${claim.confidence}%`, 20, yPos);
                yPos += 4;
            }
            
            yPos += 5; // Space between claims
        });
    }
    
    return yPos;
}

// ============================================================================
// AUTHOR ANALYSIS
// ============================================================================

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
    
    // What we analyzed/found/means sections
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

// ============================================================================
// TRANSPARENCY ANALYSIS
// ============================================================================

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
    
    // What we analyzed/found/means sections
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
    
    // Transparency lessons/indicators
    const lessons = data.transparency_lessons || data.key_indicators || data.findings || [];
    if (lessons.length > 0) {
        if (yPos > 250) {
            doc.addPage();
            yPos = 25;
        }
        
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text('Key Transparency Indicators', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        
        lessons.forEach((lesson, idx) => {
            if (yPos > 275) {
                doc.addPage();
                yPos = 25;
            }
            
            const lessonText = extractText(lesson, 200);
            
            doc.setFillColor(...serviceColor);
            doc.circle(22, yPos - 1, 0.8, 'F');
            
            const lessonLines = doc.splitTextToSize(lessonText, 165);
            doc.text(lessonLines, 26, yPos);
            yPos += (lessonLines.length * 4) + 2;
        });
        
        yPos += 5;
    }
    
    // Sources cited
    const sources = data.sources_cited || data.sources || [];
    if (sources.length > 0) {
        if (yPos > 250) {
            doc.addPage();
            yPos = 25;
        }
        
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text('Sources Referenced', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(8);
        doc.setFont('helvetica', 'normal');
        
        sources.slice(0, 15).forEach((source, idx) => {
            if (yPos > 280) {
                doc.addPage();
                yPos = 25;
            }
            
            const sourceText = extractText(source, 150);
            doc.text(`${idx + 1}. ${sourceText}`, 22, yPos);
            yPos += 4;
        });
    }
    
    return yPos;
}

// ============================================================================
// CONTENT QUALITY ANALYSIS
// ============================================================================

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
    
    // What we analyzed/found/means sections
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

// ============================================================================
// CONTRIBUTION BREAKDOWN PAGE
// ============================================================================

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
            
            // Bar background
            doc.setFillColor(240, 240, 240);
            doc.rect(20, yPos, 160, 6, 'F');
            
            // Bar fill
            const barWidth = (score / 100) * 160;
            doc.setFillColor(...service.color);
            doc.rect(20, yPos, barWidth, 6, 'F');
            
            // Score text
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

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function addFooter(doc, pageNum, totalPages) {
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(150, 150, 150);
    
    doc.text(`Page ${pageNum} of ${totalPages}`, 105, 290, { align: 'center' });
    doc.text('Generated by TruthLens - Complete AI-Powered Truth Analysis', 105, 285, { align: 'center' });
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
    if (v.includes('true') && !v.includes('false')) return colors.green;
    if (v.includes('false') || v.includes('misleading')) return colors.red;
    if (v.includes('exaggeration') || v.includes('opinion') || v.includes('rhetoric')) return colors.amber;
    return colors.orange;
}

function drawTriangle(doc, x1, y1, x2, y2, x3, y3, fillColor) {
    doc.setFillColor(...fillColor);
    doc.lines([[x2 - x1, y2 - y1], [x3 - x2, y3 - y2], [x1 - x3, y1 - y3]], x1, y1, null, 'F');
}

console.log('[PDF Generator v3.3.0] Loaded - Complete with REAL CONTENT in Executive Summary');
