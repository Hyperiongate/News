/**
 * FILE: static/js/pdf-generator.js
 * VERSION: 9.0.0 - COMPLETE PREMIUM WITH CLEAN LAYOUT + REAL BACKEND DATA
 * DATE: October 15, 2025
 * 
 * COMBINES:
 * ✅ Ultra-premium bold visual design (from v6.0.0)
 * ✅ Clean layout with proper margins (no bleeding/overlaps)
 * ✅ Real backend data extraction (uses actual field names)
 * ✅ Full-length complete implementation
 * 
 * LAYOUT SPECS:
 * - Page: 210mm x 297mm (A4)
 * - Margins: 15mm left/right, safe content zone
 * - No text bleeding outside boundaries
 * - Proper spacing between all elements
 * 
 * DATA EXTRACTION:
 * - Uses real backend fields: findings[], summary, score
 * - No fake analysis.what_we_analyzed fields
 * - Generates educational content from actual data
 */

// ============================================================================
// MAIN PDF GENERATION FUNCTION
// ============================================================================

function downloadPDFReport() {
    console.log('[Premium PDF v9.0.0] Starting premium PDF with clean layout...');
    
    // Validate jsPDF library
    if (typeof window.jspdf === 'undefined') {
        console.error('[PDF] jsPDF library not loaded');
        alert('PDF library not loaded. Please refresh the page and try again.');
        return;
    }
    
    // Validate analysis data
    const data = window.lastAnalysisData;
    if (!data) {
        console.error('[PDF] No analysis data available');
        alert('No analysis data available. Please run an analysis first.');
        return;
    }
    
    const analysisMode = data.analysis_mode || 'news';
    console.log('[Premium PDF v9.0.0] Mode:', analysisMode);
    console.log('[Premium PDF v9.0.0] Data available:', Object.keys(data));
    
    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({
            orientation: 'portrait',
            unit: 'mm',
            format: 'a4'
        });
        
        // Generate the premium PDF content
        generatePremiumPDF(doc, data);
        
        // Save with proper filename
        const timestamp = new Date().toISOString().split('T')[0];
        const modeText = analysisMode === 'news' ? 'News' : 'Transcript';
        const filename = `TruthLens-Premium-${modeText}-Report-${timestamp}.pdf`;
        
        doc.save(filename);
        
        console.log('[Premium PDF v9.0.0] ✓ Generated:', filename);
        
    } catch (error) {
        console.error('[PDF] Error:', error);
        console.error('Stack:', error.stack);
        alert('Error generating PDF. Please try again.');
    }
}

// ============================================================================
// PREMIUM PDF CONTENT ORCHESTRATION
// ============================================================================

function generatePremiumPDF(doc, data) {
    const trustScore = Math.round(data.trust_score || 0);
    const analysisMode = data.analysis_mode || 'news';
    const detailed = data.detailed_analysis || {};
    const insights = data.insights || {};
    
    // Premium color palette - VIBRANT
    const colors = {
        primary: [102, 126, 234],
        secondary: [118, 75, 162],
        accent: [59, 130, 246],
        success: [16, 185, 129],
        warning: [245, 158, 11],
        danger: [239, 68, 68],
        info: [14, 165, 233],
        text: [17, 24, 39],
        textLight: [107, 114, 128],
        purple: [147, 51, 234],
        cyan: [6, 182, 212],
        pink: [236, 72, 153],
        indigo: [79, 70, 229],
        gray: [229, 231, 235],
        darkGray: [55, 65, 81],
        background: [248, 250, 252],
        white: [255, 255, 255]
    };
    
    // Page 1: Premium Cover
    generatePremiumCoverPage(doc, data, trustScore, analysisMode, colors);
    
    // Page 2: Executive Summary
    doc.addPage();
    generatePremiumExecutiveSummary(doc, data, insights, trustScore, colors);
    
    // Page 3: Score Breakdown
    doc.addPage();
    generatePremiumScoreBreakdown(doc, detailed, trustScore, colors);
    
    // Service Pages
    if (analysisMode === 'transcript') {
        if (detailed.fact_checker) {
            doc.addPage();
            generatePremiumFactCheckPage(doc, detailed.fact_checker, colors);
        }
    } else {
        const services = [
            { key: 'source_credibility', title: 'Source Credibility Analysis', color: colors.indigo },
            { key: 'bias_detector', title: 'Bias Detection Analysis', color: colors.warning },
            { key: 'fact_checker', title: 'Fact Checking Results', color: colors.success },
            { key: 'author_analyzer', title: 'Author Credibility', color: colors.cyan },
            { key: 'transparency_analyzer', title: 'Transparency Analysis', color: colors.purple },
            { key: 'content_analyzer', title: 'Content Quality', color: colors.pink }
        ];
        
        services.forEach(service => {
            if (detailed[service.key]) {
                doc.addPage();
                generatePremiumServicePage(doc, service, detailed[service.key], colors);
            }
        });
    }
    
    // Insights Page
    doc.addPage();
    generatePremiumInsightsPage(doc, data, insights, colors);
    
    // Closing Page
    doc.addPage();
    generatePremiumClosingPage(doc, trustScore, colors);
    
    // Add page numbers
    const totalPages = doc.internal.getNumberOfPages();
    for (let i = 1; i <= totalPages; i++) {
        doc.setPage(i);
        if (i > 1 && i < totalPages) {
            addPremiumFooter(doc, i, totalPages, colors);
        }
    }
}

// ============================================================================
// PREMIUM COVER PAGE - BOLD DESIGN WITH CLEAN LAYOUT
// ============================================================================

function generatePremiumCoverPage(doc, data, trustScore, analysisMode, colors) {
    // Top gradient section - full width
    doc.setFillColor(...colors.primary);
    doc.rect(0, 0, 210, 100, 'F');
    
    // Gradient layers
    doc.setFillColor(118, 140, 235);
    doc.rect(0, 35, 210, 30, 'F');
    doc.setFillColor(128, 150, 235);
    doc.rect(0, 65, 210, 20, 'F');
    doc.setFillColor(...colors.secondary);
    doc.rect(0, 85, 210, 15, 'F');
    
    // Decorative shapes (clipped to not bleed)
    doc.setFillColor(...colors.white);
    doc.rect(165, 15, 40, 40, 'F');
    doc.setFillColor(...colors.primary);
    doc.rect(170, 20, 30, 30, 'F');
    
    // BOLD TITLE
    doc.setFontSize(54);
    doc.setTextColor(...colors.white);
    doc.setFont('helvetica', 'bold');
    doc.text('TruthLens', 105, 42, { align: 'center' });
    
    // Subtitle
    doc.setFontSize(20);
    doc.setFont('helvetica', 'normal');
    doc.text('Premium AI-Powered Truth Analysis', 105, 58, { align: 'center' });
    
    // Mode badge
    doc.setFillColor(...colors.white);
    doc.rect(60, 72, 90, 16, 'F');
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.primary);
    const modeText = analysisMode === 'news' ? 'NEWS ANALYSIS' : 'TRANSCRIPT ANALYSIS';
    doc.text(modeText, 105, 82, { align: 'center' });
    
    // White content area
    doc.setFillColor(...colors.white);
    doc.rect(0, 100, 210, 197, 'F');
    
    // MASSIVE SCORE DISPLAY - properly centered
    const centerX = 105;
    const centerY = 165;
    
    // Determine score color and grade
    let scoreColor, scoreGrade, scoreLabel;
    if (trustScore >= 90) {
        scoreColor = colors.success;
        scoreGrade = 'A+';
        scoreLabel = 'EXCELLENT';
    } else if (trustScore >= 80) {
        scoreColor = colors.success;
        scoreGrade = 'A';
        scoreLabel = 'TRUSTWORTHY';
    } else if (trustScore >= 70) {
        scoreColor = colors.info;
        scoreGrade = 'B';
        scoreLabel = 'RELIABLE';
    } else if (trustScore >= 60) {
        scoreColor = colors.accent;
        scoreGrade = 'C+';
        scoreLabel = 'MODERATE';
    } else if (trustScore >= 50) {
        scoreColor = colors.warning;
        scoreGrade = 'C';
        scoreLabel = 'QUESTIONABLE';
    } else {
        scoreColor = colors.danger;
        scoreGrade = 'F';
        scoreLabel = 'UNRELIABLE';
    }
    
    // Thick colored ring
    doc.setDrawColor(...scoreColor);
    doc.setLineWidth(18);
    doc.circle(centerX, centerY, 38, 'S');
    
    // Inner circle
    doc.setFillColor(...colors.white);
    doc.setDrawColor(...scoreColor);
    doc.setLineWidth(4);
    doc.circle(centerX, centerY, 33, 'FD');
    
    // MASSIVE SCORE NUMBER
    doc.setFontSize(58);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...scoreColor);
    doc.text(trustScore.toString(), centerX, centerY + 2, { align: 'center' });
    
    doc.setFontSize(18);
    doc.setTextColor(...colors.textLight);
    doc.text('/100', centerX, centerY + 14, { align: 'center' });
    
    // Grade badge
    doc.setFillColor(...scoreColor);
    doc.rect(centerX - 28, centerY + 33, 56, 22, 'F');
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.white);
    doc.text(scoreGrade, centerX, centerY + 48, { align: 'center' });
    
    // Score label
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...scoreColor);
    doc.text(scoreLabel, centerX, centerY + 68, { align: 'center' });
    
    // Metadata box - WITH PROPER MARGINS
    const boxY = 245;
    doc.setFillColor(...colors.background);
    doc.rect(15, boxY, 180, 42, 'F');
    doc.setDrawColor(...colors.darkGray);
    doc.setLineWidth(2);
    doc.rect(15, boxY, 180, 42, 'S');
    
    let yPos = boxY + 11;
    
    // Source
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('Source:', 20, yPos);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    const sourceText = (data.source || 'Unknown').substring(0, 48);
    doc.text(sourceText, 50, yPos);
    
    // Author
    yPos += 10;
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('Author:', 20, yPos);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    const authorText = (data.author || 'Unknown').substring(0, 48);
    doc.text(authorText, 50, yPos);
    
    // Date
    yPos += 10;
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('Analyzed:', 20, yPos);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    const dateStr = new Date().toLocaleDateString('en-US', { 
        month: 'long', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });
    doc.text(dateStr, 50, yPos);
}

// ============================================================================
// PREMIUM EXECUTIVE SUMMARY - WITH PROPER MARGINS
// ============================================================================

function generatePremiumExecutiveSummary(doc, data, insights, trustScore, colors) {
    // Bold header
    doc.setFillColor(...colors.primary);
    doc.rect(0, 0, 210, 22, 'F');
    
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.white);
    doc.text('Executive Summary', 105, 13, { align: 'center' });
    
    let yPos = 35;
    
    // Quick Stats Cards - WITH MARGINS
    const stats = [
        { label: 'Trust Score', value: `${trustScore}/100`, 
          color: trustScore >= 70 ? colors.success : trustScore >= 50 ? colors.warning : colors.danger },
        { label: 'Sources', value: data.sources_count || 'N/A', color: colors.info },
        { label: 'Claims', value: data.claims_verified || 'N/A', color: colors.success },
        { label: 'Bias', value: data.bias_level || 'Low', color: colors.warning }
    ];
    
    stats.forEach((stat, index) => {
        const x = 15 + (index * 45);
        
        // Card with thick border
        doc.setFillColor(...colors.white);
        doc.rect(x, yPos, 42, 38, 'F');
        doc.setDrawColor(...stat.color);
        doc.setLineWidth(3);
        doc.rect(x, yPos, 42, 38, 'S');
        
        // Colored header
        doc.setFillColor(...stat.color);
        doc.rect(x, yPos, 42, 7, 'F');
        
        // Value
        doc.setFontSize(18);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...stat.color);
        doc.text(String(stat.value), x + 21, yPos + 23, { align: 'center' });
        
        // Label
        doc.setFontSize(8);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...colors.text);
        doc.text(stat.label, x + 21, yPos + 33, { align: 'center' });
    });
    
    yPos += 48;
    
    // Key Findings Section - WITH PROPER MARGINS
    const boxHeight = 65;
    doc.setFillColor(245, 251, 245);
    doc.rect(15, yPos, 180, boxHeight, 'F');
    doc.setDrawColor(...colors.success);
    doc.setLineWidth(3);
    doc.rect(15, yPos, 180, boxHeight, 'S');
    
    // Accent bar
    doc.setFillColor(...colors.success);
    doc.rect(15, yPos, 7, boxHeight, 'F');
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Key Findings', 27, yPos + 11);
    
    // Extract findings from real backend data
    const findings = extractRealFindings(data);
    let fy = yPos + 20;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.text);
    
    findings.slice(0, 4).forEach(finding => {
        // Bullet
        doc.setFillColor(...colors.success);
        doc.circle(29, fy - 1.5, 2.5, 'F');
        
        // Text - properly wrapped
        const text = finding.substring(0, 100);
        const lines = doc.splitTextToSize(text, 155);
        doc.text(lines[0], 35, fy);
        fy += 11;
    });
    
    yPos += boxHeight + 12;
    
    // Service Performance - WITH MARGINS
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Analysis Performance by Service', 15, yPos);
    
    yPos += 13;
    
    const detailed = data.detailed_analysis || {};
    const services = [
        { key: 'source_credibility', label: 'Source', color: colors.indigo },
        { key: 'bias_detector', label: 'Bias', color: colors.warning },
        { key: 'fact_checker', label: 'Facts', color: colors.success },
        { key: 'author_analyzer', label: 'Author', color: colors.cyan },
        { key: 'transparency_analyzer', label: 'Transparency', color: colors.purple },
        { key: 'content_analyzer', label: 'Content', color: colors.pink }
    ];
    
    services.forEach(service => {
        if (detailed[service.key] && yPos < 245) {
            const score = getServiceScore(service.key, detailed[service.key]);
            
            // Label
            doc.setFontSize(9);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(...colors.text);
            doc.text(service.label, 18, yPos);
            
            // Score
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(...service.color);
            doc.text(`${score}/100`, 192, yPos, { align: 'right' });
            
            // Bar background
            doc.setFillColor(...colors.gray);
            doc.rect(18, yPos + 2, 147, 7, 'F');
            
            // Bar fill
            doc.setFillColor(...service.color);
            const barWidth = (score / 100) * 147;
            doc.rect(18, yPos + 2, barWidth, 7, 'F');
            
            yPos += 14;
        }
    });
    
    // Bottom Line - FIXED POSITION TO AVOID OVERLAP
    yPos = 248;
    doc.setFillColor(255, 251, 235);
    doc.rect(15, yPos, 180, 32, 'F');
    doc.setDrawColor(...colors.warning);
    doc.setLineWidth(3);
    doc.rect(15, yPos, 180, 32, 'S');
    
    doc.setFontSize(13);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('The Bottom Line', 22, yPos + 11);
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    const bottomLine = data.findings_summary || generateBottomLineSummary(trustScore);
    const lines = doc.splitTextToSize(bottomLine, 168);
    doc.text(lines.slice(0, 2), 22, yPos + 21);
}

// ============================================================================
// PREMIUM SCORE BREAKDOWN - CLEAN VISUALIZATION
// ============================================================================

function generatePremiumScoreBreakdown(doc, detailed, trustScore, colors) {
    // Header
    doc.setFillColor(...colors.primary);
    doc.rect(0, 0, 210, 22, 'F');
    
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.white);
    doc.text('Trust Score Breakdown', 105, 13, { align: 'center' });
    
    // Circular score display
    const centerX = 105;
    const centerY = 68;
    
    // Colored ring segments
    const contributions = getServiceContributions(detailed);
    let totalAngle = 0;
    
    contributions.forEach(contrib => {
        const startAngle = totalAngle;
        const sweepAngle = (contrib.percentage / 100) * 360;
        
        // Draw arc segments
        for (let i = 0; i < sweepAngle; i += 2) {
            const angle = ((startAngle + i) * Math.PI) / 180 - Math.PI/2;
            const x1 = centerX + Math.cos(angle) * 33;
            const y1 = centerY + Math.sin(angle) * 33;
            const x2 = centerX + Math.cos(angle) * 42;
            const y2 = centerY + Math.sin(angle) * 42;
            
            doc.setDrawColor(...contrib.color);
            doc.setLineWidth(3.5);
            doc.line(x1, y1, x2, y2);
        }
        
        totalAngle += sweepAngle;
    });
    
    // Center circle
    doc.setFillColor(...colors.white);
    doc.circle(centerX, centerY, 28, 'F');
    doc.setDrawColor(...colors.primary);
    doc.setLineWidth(3);
    doc.circle(centerX, centerY, 28, 'S');
    
    doc.setFontSize(34);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.primary);
    doc.text(trustScore.toString(), centerX, centerY + 3, { align: 'center' });
    
    doc.setFontSize(11);
    doc.setTextColor(...colors.textLight);
    doc.text('/100', centerX, centerY + 12, { align: 'center' });
    
    // Service Contributions List
    let yPos = 120;
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Service Contributions to Final Score', 15, yPos);
    
    yPos += 13;
    
    contributions.forEach(contrib => {
        if (yPos > 230) return;
        
        // Color box
        doc.setFillColor(...contrib.color);
        doc.rect(18, yPos - 5, 18, 9, 'F');
        
        // Name
        doc.setFontSize(10);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        doc.text(contrib.name, 40, yPos);
        
        // Percentage
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text(`${contrib.percentage}%`, 120, yPos);
        
        // Points
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...colors.textLight);
        doc.text(`${contrib.points.toFixed(1)}/${contrib.maxPoints}`, 150, yPos);
        
        yPos += 12;
    });
    
    // Score Guide
    yPos = 228;
    
    doc.setFillColor(...colors.background);
    doc.rect(15, yPos, 180, 48, 'F');
    doc.setDrawColor(...colors.darkGray);
    doc.setLineWidth(2);
    doc.rect(15, yPos, 180, 48, 'S');
    
    doc.setFontSize(13);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('What Your Score Means', 22, yPos + 11);
    
    yPos += 18;
    
    const interpretations = [
        { range: '90-100: Excellent', desc: 'Highly trustworthy', color: colors.success },
        { range: '70-89: Good', desc: 'Generally reliable', color: colors.info },
        { range: '50-69: Moderate', desc: 'Verify key claims', color: colors.warning }
    ];
    
    interpretations.forEach(interp => {
        const rangeNums = interp.range.match(/\d+/g).map(Number);
        const isActive = trustScore >= rangeNums[0] && trustScore <= rangeNums[1];
        
        if (isActive) {
            doc.setFillColor(...interp.color);
            doc.rect(18, yPos - 3, 174, 11, 'F');
            doc.setTextColor(...colors.white);
        } else {
            doc.setTextColor(...colors.text);
        }
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'bold');
        doc.text(interp.range, 22, yPos);
        
        doc.setFont('helvetica', 'normal');
        if (isActive) {
            doc.setTextColor(...colors.white);
        } else {
            doc.setTextColor(...colors.textLight);
        }
        doc.text(interp.desc, 75, yPos);
        
        yPos += 10;
    });
}

// ============================================================================
// PREMIUM SERVICE PAGE - WITH REAL BACKEND DATA
// ============================================================================

function generatePremiumServicePage(doc, service, data, colors) {
    console.log('[PDF v9.0.0] Service page:', service.key, 'Data:', data);
    
    // Header
    doc.setFillColor(...service.color);
    doc.rect(0, 0, 210, 22, 'F');
    
    doc.setFontSize(19);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.white);
    doc.text(service.title, 105, 13, { align: 'center' });
    
    let yPos = 35;
    
    // Large score card
    const score = getServiceScore(service.key, data);
    
    doc.setFillColor(...colors.white);
    doc.rect(15, yPos, 65, 55, 'F');
    doc.setDrawColor(...service.color);
    doc.setLineWidth(4);
    doc.rect(15, yPos, 65, 55, 'S');
    
    // Header bar
    doc.setFillColor(...service.color);
    doc.rect(15, yPos, 65, 9, 'F');
    
    // Score
    doc.setFontSize(36);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...service.color);
    doc.text(score.toString(), 47.5, yPos + 37, { align: 'center' });
    
    doc.setFontSize(13);
    doc.setTextColor(...colors.textLight);
    doc.text('/100', 47.5, yPos + 48, { align: 'center' });
    
    // Summary box - PROPER MARGINS
    const summaryText = generateServiceSummary(service.key, score, data);
    
    doc.setFillColor(255, 251, 235);
    doc.rect(85, yPos, 110, 55, 'F');
    doc.setDrawColor(...colors.warning);
    doc.setLineWidth(2);
    doc.rect(85, yPos, 110, 55, 'S');
    
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Summary', 90, yPos + 9);
    
    doc.setFontSize(8.5);
    doc.setFont('helvetica', 'normal');
    const lines = doc.splitTextToSize(summaryText, 100);
    doc.text(lines.slice(0, 5), 90, yPos + 18);
    
    yPos += 63;
    
    // Findings from real backend - WITH MARGINS
    if (data.findings && Array.isArray(data.findings) && data.findings.length > 0) {
        doc.setFillColor(245, 251, 245);
        doc.rect(15, yPos, 180, 55, 'F');
        doc.setDrawColor(...colors.success);
        doc.setLineWidth(3);
        doc.rect(15, yPos, 180, 55, 'F');
        
        // Accent bar
        doc.setFillColor(...colors.success);
        doc.rect(15, yPos, 7, 55, 'F');
        
        doc.setFontSize(13);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        doc.text('Key Findings', 27, yPos + 11);
        
        let fy = yPos + 20;
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        
        data.findings.slice(0, 4).forEach(finding => {
            const text = typeof finding === 'string' ? finding : 
                        finding.text || finding.finding || '';
            
            if (text && fy < yPos + 50) {
                doc.setFillColor(...colors.success);
                doc.circle(29, fy - 1.5, 2, 'F');
                
                const wrapped = doc.splitTextToSize(text.substring(0, 100), 158);
                doc.text(wrapped[0], 35, fy);
                fy += 10;
            }
        });
        
        yPos += 63;
    }
    
    // Service-specific details
    if (yPos < 230) {
        addPremiumServiceDetails(doc, service.key, data, yPos, colors);
    }
}

// ============================================================================
// PREMIUM FACT CHECK PAGE - CLEAN LAYOUT
// ============================================================================

function generatePremiumFactCheckPage(doc, data, colors) {
    console.log('[PDF v9.0.0] Fact check data:', data);
    
    // Header
    doc.setFillColor(...colors.success);
    doc.rect(0, 0, 210, 22, 'F');
    
    doc.setFontSize(19);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.white);
    doc.text('Fact Checking Results', 105, 13, { align: 'center' });
    
    let yPos = 35;
    
    const score = data.accuracy_score || data.verification_score || data.score || 0;
    const checks = data.fact_checks || data.claims || [];
    
    console.log('[PDF v9.0.0] Fact checks:', checks.length);
    
    // Summary cards
    const stats = [
        { label: 'Accuracy', value: `${score}%`, color: colors.success },
        { label: 'Analyzed', value: checks.length, color: colors.info },
        { label: 'Verified', value: data.claims_verified || 0, color: colors.success }
    ];
    
    stats.forEach((stat, index) => {
        const x = 15 + (index * 60);
        
        doc.setFillColor(...colors.white);
        doc.rect(x, yPos, 55, 42, 'F');
        doc.setDrawColor(...stat.color);
        doc.setLineWidth(3);
        doc.rect(x, yPos, 55, 42, 'S');
        
        // Header
        doc.setFillColor(...stat.color);
        doc.rect(x, yPos, 55, 7, 'F');
        
        // Value
        doc.setFontSize(22);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...stat.color);
        doc.text(String(stat.value), x + 27.5, yPos + 26, { align: 'center' });
        
        // Label
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...colors.text);
        doc.text(stat.label, x + 27.5, yPos + 36, { align: 'center' });
    });
    
    yPos += 52;
    
    // Individual checks
    if (checks.length > 0) {
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        doc.text('Verification Details', 15, yPos);
        
        yPos += 12;
        
        checks.slice(0, 4).forEach(check => {
            if (yPos > 235) return;
            
            const verdict = check.verdict || 'unverified';
            const explanation = check.explanation || check.analysis || 'No details';
            const verdictColor = getVerdictColor(verdict, colors);
            
            // Card
            doc.setFillColor(...colors.white);
            doc.rect(15, yPos, 180, 42, 'F');
            doc.setDrawColor(...colors.gray);
            doc.setLineWidth(1.5);
            doc.rect(15, yPos, 180, 42, 'S');
            
            // Verdict badge
            doc.setFillColor(...verdictColor);
            doc.rect(20, yPos + 6, 55, 12, 'F');
            
            doc.setFontSize(10);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(...colors.white);
            doc.text(verdict.toUpperCase(), 47.5, yPos + 14, { align: 'center' });
            
            // Confidence
            if (check.confidence) {
                doc.setFontSize(11);
                doc.setFont('helvetica', 'bold');
                doc.setTextColor(...verdictColor);
                doc.text(`${check.confidence}%`, 188, yPos + 14, { align: 'right' });
            }
            
            // Explanation
            doc.setFontSize(8.5);
            doc.setFont('helvetica', 'normal');
            doc.setTextColor(...colors.text);
            const lines = doc.splitTextToSize(explanation, 170);
            doc.text(lines.slice(0, 2), 20, yPos + 26);
            
            yPos += 46;
        });
    } else {
        doc.setFillColor(245, 248, 255);
        doc.rect(15, yPos, 180, 35, 'F');
        doc.setDrawColor(...colors.info);
        doc.setLineWidth(2);
        doc.rect(15, yPos, 180, 35, 'S');
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...colors.text);
        doc.text('No specific fact checks available for this content.', 22, yPos + 12);
        doc.text('The content may be opinion-based or editorial.', 22, yPos + 22);
    }
}

// ============================================================================
// PREMIUM INSIGHTS PAGE
// ============================================================================

function generatePremiumInsightsPage(doc, data, insights, colors) {
    // Header
    doc.setFillColor(...colors.purple);
    doc.rect(0, 0, 210, 22, 'F');
    
    doc.setFontSize(19);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.white);
    doc.text('Key Insights & Recommendations', 105, 13, { align: 'center' });
    
    let yPos = 35;
    
    const sections = [
        {
            title: 'Most Important Finding',
            content: insights.main_finding || insights.bottom_line || 
                    generateMainFinding(data),
            color: colors.primary
        },
        {
            title: 'Areas of Concern',
            content: insights.concerns || generateConcerns(data),
            color: colors.warning
        },
        {
            title: 'Positive Indicators',
            content: insights.positives || generatePositives(data),
            color: colors.success
        },
        {
            title: 'Recommendations',
            content: insights.recommendations || generateRecommendations(data),
            color: colors.info
        }
    ];
    
    sections.forEach(section => {
        if (yPos > 235) return;
        
        // Card
        doc.setFillColor(...colors.background);
        doc.rect(15, yPos, 180, 52, 'F');
        doc.setDrawColor(...section.color);
        doc.setLineWidth(3);
        doc.rect(15, yPos, 180, 52, 'S');
        
        // Accent bar
        doc.setFillColor(...section.color);
        doc.rect(15, yPos, 9, 52, 'F');
        
        // Title
        doc.setFontSize(13);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        doc.text(section.title, 29, yPos + 11);
        
        // Content
        doc.setFontSize(9.5);
        doc.setFont('helvetica', 'normal');
        const lines = doc.splitTextToSize(section.content, 160);
        doc.text(lines.slice(0, 3), 29, yPos + 22);
        
        yPos += 57;
    });
}

// ============================================================================
// PREMIUM CLOSING PAGE
// ============================================================================

function generatePremiumClosingPage(doc, trustScore, colors) {
    // Top gradient
    doc.setFillColor(...colors.primary);
    doc.rect(0, 0, 210, 100, 'F');
    
    doc.setFillColor(118, 140, 235);
    doc.rect(0, 35, 210, 35, 'F');
    doc.setFillColor(128, 150, 235);
    doc.rect(0, 70, 210, 30, 'F');
    
    // Thank you
    doc.setFontSize(38);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.white);
    doc.text('Thank You', 105, 52, { align: 'center' });
    
    doc.setFontSize(16);
    doc.setFont('helvetica', 'normal');
    doc.text('for using TruthLens Premium Analysis', 105, 70, { align: 'center' });
    
    // White section
    doc.setFillColor(...colors.white);
    doc.rect(0, 100, 210, 197, 'F');
    
    // Summary card
    doc.setFillColor(...colors.background);
    doc.rect(35, 135, 140, 75, 'F');
    doc.setDrawColor(...colors.primary);
    doc.setLineWidth(3);
    doc.rect(35, 135, 140, 75, 'S');
    
    doc.setFontSize(15);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Your Analysis Summary', 105, 152, { align: 'center' });
    
    const scoreColor = trustScore >= 70 ? colors.success : 
                       trustScore >= 50 ? colors.warning : colors.danger;
    
    doc.setFontSize(46);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...scoreColor);
    doc.text(`${trustScore}/100`, 105, 183, { align: 'center' });
    
    const label = trustScore >= 80 ? 'Trustworthy Content' :
                  trustScore >= 60 ? 'Reliable' : 'Questionable';
    doc.setFontSize(13);
    doc.setTextColor(...colors.textLight);
    doc.text(label, 105, 198, { align: 'center' });
    
    // CTA button
    doc.setFillColor(...colors.primary);
    doc.rect(45, 235, 120, 45, 'F');
    
    doc.setFontSize(15);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.white);
    doc.text('Continue with TruthLens', 105, 253, { align: 'center' });
    
    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');
    doc.text('Visit truthlens.ai', 105, 268, { align: 'center' });
    
    // Footer
    doc.setFontSize(9);
    doc.setTextColor(...colors.textLight);
    doc.text('© 2025 TruthLens - AI Analysis', 105, 285, { align: 'center' });
}

// ============================================================================
// HELPER FUNCTIONS - EXTRACT FROM REAL BACKEND DATA
// ============================================================================

function getServiceScore(key, data) {
    if (!data) return 0;
    
    const scoreFields = [
        'score', 'credibility_score', 'objectivity_score',
        'verification_score', 'accuracy_score', 'transparency_score',
        'quality_score', 'content_score'
    ];
    
    for (const field of scoreFields) {
        if (data[field] !== undefined && data[field] !== null) {
            return Math.round(Number(data[field]) || 0);
        }
    }
    
    return 0;
}

function extractRealFindings(data) {
    const findings = [];
    const detailed = data.detailed_analysis || {};
    
    // Extract from each service's findings array
    Object.values(detailed).forEach(service => {
        if (service && service.findings && Array.isArray(service.findings)) {
            service.findings.forEach(f => {
                const text = typeof f === 'string' ? f : f.text || f.finding || '';
                if (text) findings.push(text);
            });
        }
    });
    
    // Fallback
    if (findings.length === 0) {
        const score = data.trust_score || 0;
        findings.push(
            score >= 70 ? 'High-quality source with strong credibility' : 'Moderate credibility source',
            score >= 70 ? 'Minimal bias detected in content' : 'Some bias elements present',
            score >= 70 ? 'Facts are well-sourced' : 'Verify key claims independently'
        );
    }
    
    return findings;
}

function generateServiceSummary(key, score, data) {
    // Try to get summary from data first
    if (data.summary) return data.summary;
    if (data.findings_summary) return data.findings_summary;
    
    // Generate based on service and score
    const summaries = {
        source_credibility: score >= 70 ? 
            'This source has established credibility and a strong reputation in journalism.' :
            'This source has moderate credibility. Consider verifying key claims independently.',
        bias_detector: score >= 70 ?
            'Minimal bias detected. Content is objective and balanced.' :
            'Some bias elements present. Consider multiple perspectives for complete understanding.',
        fact_checker: score >= 70 ?
            'Facts are well-sourced and verifiable through reliable sources.' :
            'Some claims need additional verification. Cross-reference important information.',
        author_analyzer: score >= 70 ?
            'Author has strong credentials and demonstrated expertise in this subject area.' :
            'Author credentials are moderate or unclear. Verify expertise independently.',
        transparency_analyzer: score >= 70 ?
            'Strong transparency with clear sourcing and attribution throughout.' :
            'Limited transparency in some areas. Look for additional source information.',
        content_analyzer: score >= 70 ?
            'High-quality content with good structure, clear writing, and proper formatting.' :
            'Content quality is adequate but has some issues with clarity or structure.'
    };
    
    return summaries[key] || 'Analysis completed successfully with comprehensive evaluation.';
}

function generateBottomLineSummary(score) {
    if (score >= 80) {
        return 'High credibility article from a reliable source with verified facts and minimal bias. You can trust this information.';
    } else if (score >= 60) {
        return 'Generally reliable content with minor concerns. Most information can be trusted, but verify critical claims.';
    } else {
        return 'Moderate concerns identified. Verify key claims with additional sources before relying on this information.';
    }
}

function generateMainFinding(data) {
    const score = data.trust_score || 0;
    if (score >= 80) {
        return 'High credibility article from a reliable source with verified facts and strong journalistic standards.';
    } else if (score >= 60) {
        return 'Generally reliable content with good source credibility and mostly verifiable information.';
    }
    return 'Moderate reliability. Some concerns identified that warrant additional verification of key claims.';
}

function generateConcerns(data) {
    const score = data.trust_score || 0;
    if (score >= 80) {
        return 'Minimal concerns detected. The article meets high standards for credibility and accuracy.';
    } else if (score >= 60) {
        return 'Some bias indicators detected. Consider seeking additional perspectives from other sources.';
    }
    return 'Several concerns identified including potential bias, limited sourcing, or credibility issues.';
}

function generatePositives(data) {
    const score = data.trust_score || 0;
    if (score >= 80) {
        return 'Source has established credibility, facts are well-sourced, minimal bias, strong transparency.';
    } else if (score >= 60) {
        return 'Source has moderate credibility, most facts are verifiable, reasonable transparency standards.';
    }
    return 'Some positive elements present, but verification of key claims is recommended.';
}

function generateRecommendations(data) {
    const score = data.trust_score || 0;
    if (score >= 80) {
        return 'This article meets high credibility standards. You can rely on this information with confidence.';
    } else if (score >= 60) {
        return 'Cross-reference key claims with additional reputable sources for complete understanding.';
    }
    return 'Verify all important claims independently. Seek multiple sources before relying on this information.';
}

function getServiceContributions(detailed) {
    const weights = {
        source_credibility: { weight: 25, color: [79, 70, 229] },
        bias_detector: { weight: 20, color: [245, 158, 11] },
        author_analyzer: { weight: 15, color: [6, 182, 212] },
        fact_checker: { weight: 15, color: [16, 185, 129] },
        transparency_analyzer: { weight: 10, color: [147, 51, 234] },
        content_analyzer: { weight: 5, color: [236, 72, 153] },
        other: { weight: 10, color: [156, 163, 175] }
    };
    
    const contributions = [];
    
    Object.keys(weights).forEach(key => {
        if (key === 'other') {
            contributions.push({
                name: 'Other Factors',
                percentage: weights[key].weight,
                points: 0,
                maxPoints: weights[key].weight,
                color: weights[key].color
            });
        } else if (detailed[key]) {
            const score = getServiceScore(key, detailed[key]);
            const points = (score * weights[key].weight) / 100;
            
            contributions.push({
                name: key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
                percentage: weights[key].weight,
                points: points,
                maxPoints: weights[key].weight,
                color: weights[key].color
            });
        }
    });
    
    return contributions;
}

function addPremiumServiceDetails(doc, key, data, yPos, colors) {
    if (yPos > 230) return;
    
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    
    if (key === 'source_credibility') {
        doc.text('Source Details', 18, yPos);
        yPos += 9;
        
        const details = [
            ['Organization:', data.source_name || data.organization || 'Unknown'],
            ['Type:', data.source_type || data.type || 'News Source'],
            ['Founded:', data.founded || data.established_year || 'N/A'],
            ['Reputation:', data.reputation || data.credibility_level || 'N/A']
        ];
        
        details.forEach(([label, value]) => {
            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            doc.setTextColor(...colors.textLight);
            doc.text(label, 22, yPos);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(...colors.text);
            const valText = String(value).substring(0, 45);
            doc.text(valText, 65, yPos);
            yPos += 8;
        });
        
    } else if (key === 'bias_detector') {
        doc.text('Bias Indicators', 18, yPos);
        yPos += 9;
        
        const details = [
            ['Political Lean:', data.political_label || data.political_leaning || 'Center'],
            ['Sensationalism:', data.sensationalism_level || 'Low'],
            ['Objectivity:', `${data.objectivity_score || 50}/100`]
        ];
        
        details.forEach(([label, value]) => {
            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            doc.setTextColor(...colors.textLight);
            doc.text(label, 22, yPos);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(...colors.text);
            doc.text(String(value), 65, yPos);
            yPos += 8;
        });
    }
}

function getVerdictColor(verdict, colors) {
    const v = String(verdict).toLowerCase();
    
    if (v.includes('true') || v.includes('verified') || v.includes('correct')) {
        return colors.success;
    } else if (v.includes('false') || v.includes('incorrect')) {
        return colors.danger;
    } else if (v.includes('misleading') || v.includes('exagger') || v.includes('context')) {
        return colors.warning;
    }
    
    return colors.textLight;
}

function addPremiumFooter(doc, page, total, colors) {
    doc.setFontSize(8.5);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('TruthLens Premium Report', 105, 287, { align: 'center' });
    doc.text(`Page ${page} of ${total}`, 105, 292, { align: 'center' });
}

console.log('[Premium PDF v9.0.0] ✓ Loaded - Complete premium design with clean layout');
