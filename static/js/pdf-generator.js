/**
 * TruthLens PDF Generator
 * Version: 1.0.0
 * Date: October 14, 2025
 * 
 * PURPOSE:
 * Generates professional PDF reports from TruthLens analysis results
 * 
 * FEATURES:
 * - Cover page with TruthLens branding
 * - Trust score prominently displayed
 * - All 6 service analyses with scores and findings
 * - Contribution breakdown visualization
 * - Professional formatting and layout
 * 
 * DEPENDENCIES:
 * - jsPDF library (loaded from CDN in index.html)
 * - window.lastAnalysisData (set by unified-app-core.js)
 * 
 * Save as: static/js/pdf-generator.js
 */

// Global variable to store the last analysis data
window.lastAnalysisData = null;

/**
 * Main function to download PDF report
 * Called when user clicks "Download PDF Report" button
 */
function downloadPDFReport() {
    console.log('[PDF Generator] Starting PDF generation...');
    
    // Check if jsPDF is loaded
    if (typeof window.jspdf === 'undefined') {
        console.error('[PDF Generator] jsPDF library not loaded');
        alert('PDF library not loaded. Please refresh the page and try again.');
        return;
    }
    
    // Get the last analysis data
    const data = window.lastAnalysisData;
    if (!data) {
        console.error('[PDF Generator] No analysis data available');
        alert('No analysis data available. Please run an analysis first.');
        return;
    }
    
    console.log('[PDF Generator] Generating PDF with data:', data);
    
    try {
        // Initialize jsPDF
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        // Generate the PDF
        generatePDFContent(doc, data);
        
        // Create filename with date
        const timestamp = new Date().toISOString().split('T')[0];
        const mode = data.analysis_mode || 'news';
        const filename = `TruthLens-${mode.charAt(0).toUpperCase() + mode.slice(1)}-Report-${timestamp}.pdf`;
        
        // Save the PDF
        doc.save(filename);
        
        console.log('[PDF Generator] ✓ PDF generated successfully:', filename);
    } catch (error) {
        console.error('[PDF Generator] Error generating PDF:', error);
        alert('Error generating PDF: ' + error.message);
    }
}

/**
 * Generate PDF content
 */
function generatePDFContent(doc, data) {
    const trustScore = data.trust_score || 0;
    const analysisMode = data.analysis_mode || 'news';
    const detailed = data.detailed_analysis || {};
    
    // Colors (RGB)
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
    
    // Page 1: Cover Page
    generateCoverPage(doc, data, trustScore, analysisMode, colors);
    
    // Page 2: Executive Summary
    doc.addPage();
    generateExecutiveSummary(doc, data, trustScore, analysisMode, colors);
    
    // Page 3+: Service Analyses
    const services = [
        { key: 'source_credibility', title: 'Source Credibility', color: colors.blue },
        { key: 'bias_detector', title: 'Bias Detection', color: colors.orange },
        { key: 'fact_checker', title: 'Fact Checking', color: colors.blue },
        { key: 'author_analyzer', title: 'Author Analysis', color: colors.cyan },
        { key: 'transparency_analyzer', title: 'Transparency Guide', color: colors.purple },
        { key: 'content_analyzer', title: 'Content Quality', color: colors.pink }
    ];
    
    services.forEach((service, index) => {
        if (detailed[service.key]) {
            doc.addPage();
            generateServicePage(doc, service, detailed[service.key], colors);
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
    doc.text('AI-Powered Truth Analysis Report', 105, 55, { align: 'center' });
    
    // Analysis Type Badge
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
    
    // Determine score color
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
    
    // Score circle background
    doc.setFillColor(245, 245, 245);
    doc.circle(centerX, centerY, radius, 'F');
    
    // Score circle border
    doc.setDrawColor(...scoreColor);
    doc.setLineWidth(3);
    doc.circle(centerX, centerY, radius, 'S');
    
    // Trust score number
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
    
    // Article/Content Info
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Analysis Details', 105, 210, { align: 'center' });
    
    // Source
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('Source:', 30, 225);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    const source = data.source || 'Unknown';
    doc.text(source, 55, 225);
    
    // Author
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('Author:', 30, 235);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    const author = data.author || 'Unknown';
    doc.text(author, 55, 235);
    
    // Date
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.textLight);
    doc.text('Generated:', 30, 245);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    const now = new Date().toLocaleString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    doc.text(now, 55, 245);
}

/**
 * Generate executive summary page
 */
function generateExecutiveSummary(doc, data, trustScore, analysisMode, colors) {
    // Page title
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.primary);
    doc.text('Executive Summary', 20, 25);
    
    // Divider line
    doc.setDrawColor(...colors.primary);
    doc.setLineWidth(0.5);
    doc.line(20, 30, 190, 30);
    
    let yPos = 45;
    
    // Key Findings Section
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Key Findings', 20, yPos);
    yPos += 10;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.text);
    
    const summary = data.article_summary || data.findings_summary || 'Analysis complete. See detailed service breakdowns below.';
    const summaryLines = doc.splitTextToSize(summary, 170);
    doc.text(summaryLines, 20, yPos);
    yPos += (summaryLines.length * 5) + 10;
    
    // Analysis Overview
    if (yPos > 250) {
        doc.addPage();
        yPos = 25;
    }
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Analysis Overview', 20, yPos);
    yPos += 10;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    const overviewText = `This ${analysisMode} analysis was conducted using TruthLens's 6 advanced AI services. Each service evaluates different aspects of credibility, accuracy, and transparency. The overall trust score of ${Math.round(trustScore)}/100 is calculated based on weighted contributions from all services.`;
    const overviewLines = doc.splitTextToSize(overviewText, 170);
    doc.text(overviewLines, 20, yPos);
    yPos += (overviewLines.length * 5) + 15;
    
    // Service Scores Summary Table
    if (yPos > 230) {
        doc.addPage();
        yPos = 25;
    }
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Service Scores', 20, yPos);
    yPos += 8;
    
    const detailed = data.detailed_analysis || {};
    const services = [
        { key: 'source_credibility', title: 'Source Credibility', scoreKey: 'score' },
        { key: 'bias_detector', title: 'Bias Detection', scoreKey: 'objectivity_score' },
        { key: 'fact_checker', title: 'Fact Checking', scoreKey: 'accuracy_score' },
        { key: 'author_analyzer', title: 'Author Analysis', scoreKey: 'credibility_score' },
        { key: 'transparency_analyzer', title: 'Transparency Guide', scoreKey: 'transparency_score' },
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
            
            // Alternating row colors
            if (index % 2 === 0) {
                doc.setFillColor(250, 250, 250);
                doc.rect(20, yPos, 170, 7, 'F');
            }
            
            doc.setTextColor(...colors.text);
            doc.text(service.title, 25, yPos + 5);
            
            // Color code the score
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
 * Generate individual service page
 */
function generateServicePage(doc, service, serviceData, colors) {
    // Service title with colored bar
    doc.setFillColor(...service.color);
    doc.rect(0, 0, 210, 15, 'F');
    
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text(service.title, 20, 10);
    
    let yPos = 30;
    
    // Extract score
    let score = 0;
    if (service.key === 'source_credibility') {
        score = serviceData.credibility_score || serviceData.score || 0;
    } else if (service.key === 'bias_detector') {
        score = serviceData.objectivity_score || serviceData.score || 0;
    } else if (service.key === 'fact_checker') {
        score = serviceData.verification_score || serviceData.accuracy_score || serviceData.score || 0;
    } else if (service.key === 'author_analyzer') {
        score = serviceData.credibility_score || serviceData.score || 0;
    } else if (service.key === 'transparency_analyzer') {
        score = serviceData.transparency_score || serviceData.score || 0;
    } else if (service.key === 'content_analyzer') {
        score = serviceData.quality_score || serviceData.score || 0;
    }
    
    // Score badge
    doc.setFontSize(36);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...service.color);
    doc.text(`${Math.round(score)}`, 30, yPos);
    
    doc.setFontSize(14);
    doc.setTextColor(...colors.textLight);
    doc.text('/100', 50, yPos);
    yPos += 15;
    
    // Service-specific content
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.text);
    doc.text('Analysis', 20, yPos);
    yPos += 8;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    
    // Service-specific findings
    let findings = '';
    
    if (service.key === 'source_credibility') {
        const org = serviceData.organization || serviceData.source || 'Unknown';
        const reputation = serviceData.credibility || serviceData.reputation || 'Unknown';
        const established = serviceData.established_year || serviceData.founded || 'Unknown';
        const awards = serviceData.awards || 'N/A';
        findings = `Organization: ${org}\nReputation: ${reputation}\nEstablished: ${established}\nAwards: ${awards}\n\nThis source has been evaluated for historical accuracy, editorial standards, and overall credibility in journalism.`;
    } else if (service.key === 'bias_detector') {
        const political = serviceData.political_label || serviceData.political_leaning || 'Center';
        const objectivity = serviceData.objectivity_score || score;
        const sensationalism = serviceData.sensationalism_level || 'Unknown';
        const details = serviceData.details || {};
        const loadedLang = details.loaded_language_count || 0;
        findings = `Political Lean: ${political}\nObjectivity Score: ${Math.round(objectivity)}/100\nSensationalism: ${sensationalism}\nLoaded Language Instances: ${loadedLang}\n\nThe analysis examines political bias, loaded language, sensationalism, and framing techniques to provide a comprehensive view of objectivity.`;
    } else if (service.key === 'fact_checker') {
        const claimsChecked = serviceData.claims_checked || serviceData.claims_found || 0;
        const claimsVerified = serviceData.claims_verified || 0;
        const accuracyScore = serviceData.accuracy_score || serviceData.verification_score || score;
        findings = `Claims Analyzed: ${claimsChecked}\nClaims Verified: ${claimsVerified}\nAccuracy Score: ${Math.round(accuracyScore)}%\n\nOur fact-checking service verifies specific claims using authoritative sources and cross-references multiple databases.`;
        
        // Add fact check details if available
        const factChecks = serviceData.fact_checks || serviceData.claims || [];
        if (factChecks.length > 0 && yPos < 200) {
            findings += '\n\nTop Findings:';
            factChecks.slice(0, 3).forEach((check, idx) => {
                const verdict = check.verdict || 'unverified';
                const explanation = check.explanation || check.analysis || 'No details available';
                // Truncate long explanations
                const shortExplanation = explanation.length > 100 ? explanation.substring(0, 97) + '...' : explanation;
                findings += `\n${idx + 1}. ${verdict.toUpperCase()}: ${shortExplanation}`;
            });
        }
    } else if (service.key === 'author_analyzer') {
        const authorName = serviceData.name || serviceData.primary_author || serviceData.author_name || 'Unknown Author';
        const position = serviceData.position || 'Journalist';
        const organization = serviceData.organization || serviceData.domain || 'News Organization';
        const expertise = serviceData.expertise_level || 'Verified';
        const experience = serviceData.years_experience || serviceData.experience || 'Unknown';
        findings = `Author: ${authorName}\nPosition: ${position}\nOrganization: ${organization}\nExpertise Level: ${expertise}\nExperience: ${experience}\nCredibility: ${Math.round(score)}/100\n\nAnalysis includes author background, expertise, track record, and professional credentials.`;
    } else if (service.key === 'transparency_analyzer') {
        const level = serviceData.transparency_level || serviceData.level || 'Moderate';
        const articleType = serviceData.article_type || 'News Report';
        findings = `Transparency Level: ${level}\nArticle Type: ${articleType}\nScore: ${Math.round(score)}/100\n\nEvaluates source attribution, citation quality, disclosure statements, and verifiable claims. Higher scores indicate better transparency practices.`;
        
        // Add key lessons if available
        const lessons = serviceData.transparency_lessons || [];
        if (lessons.length > 0 && yPos < 200) {
            findings += '\n\nKey Transparency Indicators:';
            lessons.slice(0, 3).forEach((lesson, idx) => {
                const shortLesson = lesson.length > 80 ? lesson.substring(0, 77) + '...' : lesson;
                findings += `\n${idx + 1}. ${shortLesson}`;
            });
        }
    } else if (service.key === 'content_analyzer') {
        const readability = serviceData.readability_level || serviceData.readability || 'Unknown';
        const wordCount = serviceData.word_count || 0;
        const qualityScore = serviceData.quality_score || score;
        findings = `Quality Score: ${Math.round(qualityScore)}/100\nReadability Level: ${readability}\nWord Count: ${wordCount.toLocaleString()}\n\nAnalyzes content structure, clarity, depth, grammar, and overall writing quality using multiple metrics.`;
    }
    
    const findingsLines = doc.splitTextToSize(findings, 170);
    doc.text(findingsLines, 20, yPos);
    yPos += (findingsLines.length * 5) + 10;
    
    // Additional insights if available - properly handle different data types
    if (yPos < 240) {
        let insightsText = '';
        
        // Try different fields for insights
        if (serviceData.insights) {
            if (typeof serviceData.insights === 'string') {
                insightsText = serviceData.insights;
            } else if (Array.isArray(serviceData.insights)) {
                insightsText = serviceData.insights.join('\n');
            }
        } else if (serviceData.analysis && typeof serviceData.analysis === 'string') {
            insightsText = serviceData.analysis;
        } else if (serviceData.summary && typeof serviceData.summary === 'string') {
            insightsText = serviceData.summary;
        } else if (serviceData.explanation && typeof serviceData.explanation === 'string') {
            insightsText = serviceData.explanation;
        }
        
        // Only display if we have valid text
        if (insightsText && insightsText.length > 0 && insightsText !== '[object Object]') {
            doc.setFontSize(12);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(...colors.text);
            doc.text('Additional Insights', 20, yPos);
            yPos += 8;
            
            doc.setFontSize(10);
            doc.setFont('helvetica', 'normal');
            
            // Truncate if too long
            if (insightsText.length > 500) {
                insightsText = insightsText.substring(0, 497) + '...';
            }
            
            const insightLines = doc.splitTextToSize(insightsText, 170);
            doc.text(insightLines, 20, yPos);
        }
    }
}

/**
 * Generate contribution breakdown page
 */
function generateContributionPage(doc, detailed, trustScore, colors) {
    // Page title
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...colors.primary);
    doc.text('Score Contribution Breakdown', 20, 25);
    
    // Divider line
    doc.setDrawColor(...colors.primary);
    doc.setLineWidth(0.5);
    doc.line(20, 30, 190, 30);
    
    let yPos = 45;
    
    // Explanation
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...colors.text);
    const explanation = 'Each service contributes to the overall trust score based on its weighted importance. Below is the breakdown showing how each service contributed to the final score.';
    const explLines = doc.splitTextToSize(explanation, 170);
    doc.text(explLines, 20, yPos);
    yPos += (explLines.length * 5) + 15;
    
    // Contribution bars
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
            
            // Extract score
            let score = 0;
            if (service.key === 'source_credibility') {
                score = serviceData.credibility_score || serviceData.score || 0;
            } else if (service.key === 'bias_detector') {
                score = serviceData.objectivity_score || serviceData.score || 0;
            } else if (service.key === 'fact_checker') {
                score = serviceData.verification_score || serviceData.accuracy_score || serviceData.score || 0;
            } else if (service.key === 'author_analyzer') {
                score = serviceData.credibility_score || serviceData.score || 0;
            } else if (service.key === 'transparency_analyzer') {
                score = serviceData.transparency_score || serviceData.score || 0;
            } else if (service.key === 'content_analyzer') {
                score = serviceData.quality_score || serviceData.score || 0;
            }
            
            const contribution = (score * service.weight).toFixed(1);
            const maxContribution = service.weight * 100;
            
            // Service name
            doc.setFontSize(10);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(...colors.text);
            doc.text(service.title, 20, yPos);
            
            // Weight percentage
            doc.setFont('helvetica', 'normal');
            doc.setTextColor(...colors.textLight);
            doc.text(`${Math.round(service.weight * 100)}%`, 180, yPos);
            yPos += 5;
            
            // Background bar
            doc.setFillColor(240, 240, 240);
            doc.rect(20, yPos, 160, 6, 'F');
            
            // Filled bar (proportional to score)
            const barWidth = (score / 100) * 160;
            doc.setFillColor(...service.color);
            doc.rect(20, yPos, barWidth, 6, 'F');
            
            // Score label
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
    
    // Total Score Summary
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
    
    // Page number
    doc.text(`Page ${pageNum} of ${totalPages}`, 105, 290, { align: 'center' });
    
    // Generated by TruthLens
    doc.text('Generated by TruthLens - AI-Powered Truth Analysis', 105, 285, { align: 'center' });
}

/**
 * Hook into the unified-app-core to capture analysis data
 * Override the displayResults function to store data
 */
(function() {
    // Wait for UnifiedTruthLensAnalyzer to be defined
    if (typeof UnifiedTruthLensAnalyzer !== 'undefined') {
        const originalDisplayResults = UnifiedTruthLensAnalyzer.prototype.displayResults;
        
        UnifiedTruthLensAnalyzer.prototype.displayResults = function(data) {
            // Store the data globally for PDF generation
            window.lastAnalysisData = data;
            console.log('[PDF Generator] Analysis data captured:', data);
            
            // Call the original function
            originalDisplayResults.call(this, data);
        };
        
        console.log('[PDF Generator] Successfully hooked into analysis results');
    } else {
        console.warn('[PDF Generator] UnifiedTruthLensAnalyzer not found yet, will retry');
        setTimeout(arguments.callee, 100);
    }
})();

console.log('[PDF Generator] v1.0.0 loaded successfully');
