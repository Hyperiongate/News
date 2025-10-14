/**
 * TruthLens PDF Generator - COMPLETE EDITION
 * Version: 2.0.0
 * Date: October 14, 2025
 * 
 * CHANGES FROM 1.0.0:
 * - NOW INCLUDES: ALL detailed analysis data from each service
 * - EXPANDED: Fact-checking details with all claims and verdicts
 * - ADDED: Complete bias analysis with loaded language examples
 * - ENHANCED: Full transparency analysis with all sources and citations
 * - IMPROVED: Author analysis with complete credentials and experience
 * - DETAILED: Content quality metrics and readability scores
 * - COMPREHENSIVE: Source credibility with full domain analysis
 * - MULTI-PAGE: Services expanded to multiple pages when needed
 * 
 * Save as: static/js/pdf-generator.js (REPLACE existing file)
 */

// Global variable to store the last analysis data
window.lastAnalysisData = null;

/**
 * Main function to download PDF report
 */
function downloadPDFReport() {
    console.log('[PDF Generator] Starting comprehensive PDF generation...');
    
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
        alert('Error generating PDF: ' + error.message);
    }
}

/**
 * Generate complete PDF content with ALL analysis data
 */
function generateCompletePDFContent(doc, data) {
    const trustScore = data.trust_score || 0;
    const analysisMode = data.analysis_mode || 'news';
    const detailed = data.detailed_analysis || {};
    const analysis = data.analysis || {};
    const article = data.article || {};
    
    console.log('[PDF] Detailed analysis:', detailed);
    console.log('[PDF] Article data:', article);
    console.log('[PDF] Analysis data:', analysis);
    
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
    generateCoverPage(doc, data, article, trustScore, analysisMode, colors);
    
    // Page 2: Executive Summary
    doc.addPage();
    generateExecutiveSummary(doc, data, analysis, trustScore, analysisMode, colors);
    
    // Page 3+: Article Overview (if available)
    if (article && (article.excerpt || article.word_count)) {
        doc.addPage();
        generateArticleOverview(doc, article, colors);
    }
    
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

/**
 * Generate cover page
 */
function generateCoverPage(doc, data, article, trustScore, analysisMode, colors) {
    // Purple gradient background
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
    
    // Article Info
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Analysis Details', 105, 210, { align: 'center' });
    
    let yPos = 225;
    
    // Source/Domain
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('Source:', 30, yPos);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    const source = article.domain || data.source || 'Unknown';
    doc.text(source.substring(0, 50), 55, yPos);
    yPos += 10;
    
    // Author
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('Author:', 30, yPos);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    const author = article.author || data.author || 'Unknown';
    doc.text(author.substring(0, 50), 55, yPos);
    yPos += 10;
    
    // Title (if available)
    if (article.title) {
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...colors.textLight);
        doc.text('Title:', 30, yPos);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        const titleText = article.title.substring(0, 80);
        const titleLines = doc.splitTextToSize(titleText, 120);
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

/**
 * Generate executive summary
 */
function generateExecutiveSummary(doc, data, analysis, trustScore, analysisMode, colors) {
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.primary);
    doc.text('Executive Summary', 20, 25);
    
    doc.setDrawColor(...colors.primary);
    doc.setLineWidth(0.5);
    doc.line(20, 30, 190, 30);
    
    let yPos = 45;
    
    // Key Findings
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Key Findings', 20, yPos);
    yPos += 10;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    
    const summary = analysis.summary || data.article_summary || data.findings_summary || 'Complete comprehensive analysis conducted across all services.';
    const summaryLines = doc.splitTextToSize(summary, 170);
    doc.text(summaryLines, 20, yPos);
    yPos += (summaryLines.length * 5) + 15;
    
    // Key Findings List (if available)
    if (analysis.key_findings && Array.isArray(analysis.key_findings) && analysis.key_findings.length > 0) {
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.text('Notable Issues', 20, yPos);
        yPos += 8;
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        
        analysis.key_findings.slice(0, 5).forEach(finding => {
            if (yPos > 250) {
                doc.addPage();
                yPos = 25;
            }
            
            const severityColor = finding.severity === 'high' ? colors.red : 
                                 finding.severity === 'medium' ? colors.orange : colors.blue;
            
            doc.setFillColor(...severityColor);
            doc.circle(22, yPos - 1, 1, 'F');
            
            const findingText = finding.text || '';
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

/**
 * Generate article overview page
 */
function generateArticleOverview(doc, article, colors) {
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.primary);
    doc.text('Article Overview', 20, 25);
    
    doc.setDrawColor(...colors.primary);
    doc.setLineWidth(0.5);
    doc.line(20, 30, 190, 30);
    
    let yPos = 45;
    
    // Title
    if (article.title) {
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        doc.text('Title', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        const titleLines = doc.splitTextToSize(article.title, 170);
        doc.text(titleLines, 20, yPos);
        yPos += (titleLines.length * 5) + 10;
    }
    
    // Metadata
    const metadata = [];
    if (article.author) metadata.push(['Author', article.author]);
    if (article.publish_date) metadata.push(['Published', article.publish_date]);
    if (article.domain) metadata.push(['Domain', article.domain]);
    if (article.word_count) metadata.push(['Word Count', article.word_count.toLocaleString() + ' words']);
    
    if (metadata.length > 0) {
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.text('Article Information', 20, yPos);
        yPos += 8;
        
        doc.setFontSize(9);
        metadata.forEach(([label, value]) => {
            doc.setFont('helvetica', 'normal');
            doc.setTextColor(...colors.textLight);
            doc.text(label + ':', 25, yPos);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(...colors.text);
            const valueText = String(value).substring(0, 60);
            doc.text(valueText, 60, yPos);
            yPos += 6;
        });
        yPos += 10;
    }
    
    // Excerpt
    if (article.excerpt && yPos < 250) {
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...colors.text);
        doc.text('Article Excerpt', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'italic');
        const excerptLines = doc.splitTextToSize(article.excerpt, 170);
        doc.text(excerptLines, 20, yPos);
    }
}

/**
 * Generate COMPLETE service pages with ALL details
 * This may span multiple pages for data-rich services
 */
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

/**
 * Complete Source Credibility Analysis
 */
function generateSourceCredibilityComplete(doc, data, yPos, colors, serviceColor) {
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Source Information', 20, yPos);
    yPos += 8;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    
    const fields = [
        ['Organization', data.organization || data.source || 'Unknown'],
        ['Domain', data.domain || 'N/A'],
        ['Reputation', data.credibility_level || data.credibility || 'Unknown'],
        ['Credibility Score', `${Math.round(data.credibility_score || 0)}/100`],
        ['Established', data.established_year || data.founded || 'Unknown'],
        ['Country', data.country || 'Unknown'],
        ['Awards', data.awards || 'N/A']
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
    
    // Analysis details - FIXED to handle objects properly
    let analysisText = '';
    
    // Try different fields for analysis text
    if (data.what_it_means && typeof data.what_it_means === 'string') {
        analysisText = data.what_it_means;
    } else if (data.explanation && typeof data.explanation === 'string') {
        analysisText = data.explanation;
    } else if (data.analysis && typeof data.analysis === 'string') {
        analysisText = data.analysis;
    } else if (data.details && typeof data.details === 'string') {
        analysisText = data.details;
    } else if (data.summary && typeof data.summary === 'string') {
        analysisText = data.summary;
    }
    
    // Only display if we have valid text
    if (analysisText && analysisText.length > 10) {
        if (yPos > 250) {
            doc.addPage();
            yPos = 25;
        }
        
        doc.setFontSize(12);
        doc.setFont('helvetica', 'bold');
        doc.text('Detailed Analysis', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        const analysisLines = doc.splitTextToSize(analysisText, 170);
        doc.text(analysisLines, 20, yPos);
        yPos += analysisLines.length * 4;
    }
    
    return yPos;
}

/**
 * Complete Bias Detection Analysis
 */
function generateBiasDetectionComplete(doc, data, yPos, colors, serviceColor) {
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Bias Analysis Summary', 20, yPos);
    yPos += 8;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    
    const fields = [
        ['Political Leaning', data.political_label || data.political_leaning || 'Center'],
        ['Objectivity Score', `${Math.round(data.objectivity_score || 0)}/100`],
        ['Sensationalism', data.sensationalism_level || 'Low'],
        ['Bias Rating', data.bias_rating || 'Minimal']
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
    
    yPos += 5;
    
    // Loaded Language Examples
    const details = data.details || {};
    const loadedLanguage = details.loaded_language_examples || data.loaded_language_examples || [];
    
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
            
            const exampleText = typeof example === 'string' ? example : 
                              example.phrase || example.text || JSON.stringify(example);
            
            doc.setFillColor(...serviceColor);
            doc.circle(22, yPos - 1, 0.8, 'F');
            
            const exLines = doc.splitTextToSize(exampleText, 165);
            doc.text(exLines, 26, yPos);
            yPos += (exLines.length * 4) + 2;
        });
        
        yPos += 5;
    }
    
    // Framing Techniques
    const framing = details.framing_techniques || data.framing_techniques || [];
    if (framing.length > 0) {
        if (yPos > 250) {
            doc.addPage();
            yPos = 25;
        }
        
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text('Framing Techniques Detected', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        
        framing.slice(0, 8).forEach(technique => {
            if (yPos > 275) {
                doc.addPage();
                yPos = 25;
            }
            
            const techText = typeof technique === 'string' ? technique :
                           technique.technique || JSON.stringify(technique);
            
            doc.setFillColor(...serviceColor);
            doc.circle(22, yPos - 1, 0.8, 'F');
            
            const techLines = doc.splitTextToSize(techText, 165);
            doc.text(techLines, 26, yPos);
            yPos += (techLines.length * 4) + 2;
        });
    }
    
    // Overall explanation
    if (data.explanation || data.analysis) {
        if (yPos > 250) {
            doc.addPage();
            yPos = 25;
        }
        
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text('Analysis Explanation', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        const explText = data.explanation || data.analysis;
        const explLines = doc.splitTextToSize(String(explText), 170);
        doc.text(explLines, 20, yPos);
        yPos += explLines.length * 4;
    }
    
    return yPos;
}

/**
 * Complete Fact Checking Analysis with ALL claims
 */
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
    
    // COMPLETE CLAIMS LIST - ALL CLAIMS WITH VERDICTS
    const claims = data.fact_checks || data.claims || data.claims_analyzed || [];
    
    if (claims.length > 0) {
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
            const claimText = claim.claim || claim.text || claim.statement || '';
            const claimLines = doc.splitTextToSize(claimText, 170);
            doc.text(claimLines, 20, yPos);
            yPos += (claimLines.length * 4) + 3;
            
            // Explanation/Analysis
            const explanation = claim.explanation || claim.analysis || claim.reason || '';
            if (explanation) {
                doc.setFont('helvetica', 'italic');
                doc.setTextColor(...colors.textLight);
                doc.setFontSize(8);
                const explLines = doc.splitTextToSize(String(explanation).substring(0, 300), 170);
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

/**
 * Complete Author Analysis
 */
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
        ['Credibility Score', `${Math.round(data.credibility_score || 0)}/100`],
        ['Expertise Level', data.expertise_level || data.expertise || 'Unknown'],
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
    
    // Educational background
    if (data.education || data.credentials) {
        if (yPos > 260) {
            doc.addPage();
            yPos = 25;
        }
        
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text('Education & Credentials', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        const eduText = data.education || data.credentials;
        const eduLines = doc.splitTextToSize(String(eduText), 170);
        doc.text(eduLines, 20, yPos);
        yPos += eduLines.length * 4 + 8;
    }
    
    // Notable works or publications
    if (data.notable_works || data.publications) {
        if (yPos > 260) {
            doc.addPage();
            yPos = 25;
        }
        
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text('Notable Works', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        const works = data.notable_works || data.publications;
        const worksText = Array.isArray(works) ? works.join(', ') : String(works);
        const worksLines = doc.splitTextToSize(worksText, 170);
        doc.text(worksLines, 20, yPos);
        yPos += worksLines.length * 4 + 8;
    }
    
    // Analysis summary
    if (data.analysis || data.summary) {
        if (yPos > 250) {
            doc.addPage();
            yPos = 25;
        }
        
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text('Analysis', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        const analysisText = data.analysis || data.summary;
        const analysisLines = doc.splitTextToSize(String(analysisText), 170);
        doc.text(analysisLines, 20, yPos);
        yPos += analysisLines.length * 4;
    }
    
    return yPos;
}

/**
 * Complete Transparency Analysis
 */
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
        ['Transparency Score', `${Math.round(data.transparency_score || 0)}/100`],
        ['Article Type', data.article_type || data.content_type || 'News Report'],
        ['Sources Cited', data.sources_count || data.source_count || 'Unknown'],
        ['Direct Quotes', data.quotes_count || data.quote_count || 'Unknown']
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
            
            const lessonText = typeof lesson === 'string' ? lesson :
                             lesson.text || lesson.lesson || JSON.stringify(lesson);
            
            doc.setFillColor(...serviceColor);
            doc.circle(22, yPos - 1, 0.8, 'F');
            
            const lessonLines = doc.splitTextToSize(lessonText, 165);
            doc.text(lessonLines, 26, yPos);
            yPos += (lessonLines.length * 4) + 2;
        });
        
        yPos += 5;
    }
    
    // Sources cited (if detailed list available)
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
            
            const sourceText = typeof source === 'string' ? source :
                             source.name || source.source || JSON.stringify(source);
            
            doc.text(`${idx + 1}. ${sourceText}`, 22, yPos);
            yPos += 4;
        });
    }
    
    return yPos;
}

/**
 * Complete Content Quality Analysis
 */
function generateContentQualityComplete(doc, data, yPos, colors, serviceColor) {
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Content Quality Metrics', 20, yPos);
    yPos += 8;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    
    const fields = [
        ['Quality Score', `${Math.round(data.quality_score || 0)}/100`],
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
    
    // Readability metrics
    if (data.readability_scores || data.metrics) {
        if (yPos > 250) {
            doc.addPage();
            yPos = 25;
        }
        
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text('Readability Metrics', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        
        const metrics = data.readability_scores || data.metrics;
        Object.entries(metrics).forEach(([key, value]) => {
            if (yPos > 275) {
                doc.addPage();
                yPos = 25;
            }
            
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            doc.setTextColor(...colors.textLight);
            doc.text(label + ':', 25, yPos);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(...colors.text);
            doc.text(String(value), 100, yPos);
            doc.setFont('helvetica', 'normal');
            yPos += 5;
        });
    }
    
    // Quality analysis
    if (data.analysis || data.summary) {
        if (yPos > 250) {
            doc.addPage();
            yPos = 25;
        }
        
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text('Quality Analysis', 20, yPos);
        yPos += 7;
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        const analysisText = data.analysis || data.summary;
        const analysisLines = doc.splitTextToSize(String(analysisText), 170);
        doc.text(analysisLines, 20, yPos);
        yPos += analysisLines.length * 4;
    }
    
    return yPos;
}

/**
 * Generate contribution breakdown page
 */
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

/**
 * Add footer to page
 */
function addFooter(doc, pageNum, totalPages) {
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(150, 150, 150);
    
    doc.text(`Page ${pageNum} of ${totalPages}`, 105, 290, { align: 'center' });
    doc.text('Generated by TruthLens - Complete AI-Powered Truth Analysis', 105, 285, { align: 'center' });
}

/**
 * Helper: Extract score from service data
 */
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

/**
 * Helper: Get verdict color
 */
function getVerdictColor(verdict, colors) {
    const v = verdict.toLowerCase();
    if (v.includes('true') && !v.includes('false')) return colors.green;
    if (v.includes('false') || v.includes('misleading')) return colors.red;
    if (v.includes('exaggeration') || v.includes('opinion') || v.includes('rhetoric')) return colors.amber;
    return colors.orange;
}

/**
 * Hook into unified-app-core to capture analysis data
 */
(function() {
    if (typeof UnifiedTruthLensAnalyzer !== 'undefined') {
        const originalDisplayResults = UnifiedTruthLensAnalyzer.prototype.displayResults;
        
        UnifiedTruthLensAnalyzer.prototype.displayResults = function(data) {
            window.lastAnalysisData = data;
            console.log('[PDF Generator] Complete analysis data captured for comprehensive PDF:', data);
            
            originalDisplayResults.call(this, data);
        };
        
        console.log('[PDF Generator] Successfully hooked into analysis results');
    } else {
        console.warn('[PDF Generator] UnifiedTruthLensAnalyzer not found, will retry');
        setTimeout(arguments.callee, 100);
    }
})();

console.log('[PDF Generator] v2.0.0 Complete Edition loaded successfully');
