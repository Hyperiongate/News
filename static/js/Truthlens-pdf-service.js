// truthlens-pdf-service.js - PDF Generation Service Module
// Handles PDF generation for analysis reports

const TruthLensPDFService = {
    // ============================================================================
    // PDF Generation Methods
    // ============================================================================

    async downloadPDF() {
        if (!this.currentAnalysis || !this.currentAnalysis.analysis || !this.currentAnalysis.article) {
            this.showError('No analysis available to download');
            return;
        }
        
        this.showLoading();
        
        try {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            
            // Generate comprehensive PDF with all analysis details
            this.generateComprehensivePDF(doc);
            
            // Save the PDF
            const fileName = `truthlens-analysis-${Date.now()}.pdf`;
            doc.save(fileName);
            
        } catch (error) {
            console.error('PDF generation error:', error);
            this.showError('Failed to generate PDF report. Please try again.');
        } finally {
            this.hideLoading();
        }
    },

    generateComprehensivePDF(doc) {
        const { article, analysis, detailed_analysis } = this.currentAnalysis;
        let yPosition = 20;
        const lineHeight = 7;
        const pageHeight = doc.internal.pageSize.height;
        const pageWidth = doc.internal.pageSize.width;
        const margin = 20;
        const contentWidth = pageWidth - (2 * margin);
        
        // Helper function to add text with page break check
        const addText = (text, fontSize = 12, fontStyle = 'normal', indent = 0) => {
            doc.setFontSize(fontSize);
            doc.setFont(undefined, fontStyle);
            
            const lines = doc.splitTextToSize(text, contentWidth - indent);
            
            lines.forEach(line => {
                if (yPosition > pageHeight - 30) {
                    doc.addPage();
                    yPosition = 20;
                }
                doc.text(line, margin + indent, yPosition);
                yPosition += fontSize === 12 ? lineHeight : lineHeight + 2;
            });
        };
        
        // Title Page
        doc.setFillColor(99, 102, 241);
        doc.rect(0, 0, pageWidth, 60, 'F');
        doc.setTextColor(255, 255, 255);
        addText('TruthLens AI Analysis Report', 24, 'bold');
        yPosition += 10;
        addText(new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        }), 12);
        
        // Reset text color
        doc.setTextColor(0, 0, 0);
        yPosition = 80;
        
        // Article Information
        addText('ARTICLE INFORMATION', 16, 'bold');
        yPosition += 5;
        
        addText(`Title: ${article.title || 'Untitled'}`, 12);
        addText(`Author: ${article.author || 'Unknown'}`, 12);
        addText(`Source: ${article.domain || article.source || 'Unknown'}`, 12);
        if (article.publish_date) {
            addText(`Published: ${new Date(article.publish_date).toLocaleDateString()}`, 12);
        }
        
        yPosition += 10;
        
        // Executive Summary
        addText('EXECUTIVE SUMMARY', 16, 'bold');
        yPosition += 5;
        
        const trustScore = analysis.trust_score || 0;
        addText(`Overall Trust Score: ${trustScore}/100`, 14, 'bold');
        addText(this.getTrustSummaryExplanation(trustScore, analysis.trust_level, this.currentAnalysis), 12);
        
        yPosition += 10;
        
        // Key Findings
        let findings = [];
        if (analysis.key_findings && Array.isArray(analysis.key_findings)) {
            findings = analysis.key_findings.map(finding => ({
                type: finding.severity === 'high' ? 'negative' : 
                      finding.severity === 'low' ? 'positive' : 'warning',
                title: finding.finding || finding.type || 'Finding',
                explanation: finding.text || finding.message || ''
            }));
        } else {
            findings = this.generateMeaningfulFindings(this.currentAnalysis);
        }
        
        if (findings.length > 0) {
            addText('KEY FINDINGS', 16, 'bold');
            yPosition += 5;
            
            findings.forEach(finding => {
                const icon = finding.type === 'positive' ? '✓' : 
                           finding.type === 'negative' ? '✗' : '!';
                addText(`${icon} ${finding.title}`, 12, 'bold');
                addText(finding.explanation, 11, 'normal', 10);
                yPosition += 3;
            });
        }
        
        // New page for detailed analysis
        doc.addPage();
        yPosition = 20;
        
        addText('DETAILED ANALYSIS', 18, 'bold');
        yPosition += 10;
        
        // Process each service with meaningful content
        const services = [
            { id: 'source_credibility', name: 'Source Credibility' },
            { id: 'author_analyzer', name: 'Author Analysis' },
            { id: 'bias_detector', name: 'Bias Detection' },
            { id: 'fact_checker', name: 'Fact Verification' },
            { id: 'transparency_analyzer', name: 'Transparency Analysis' },
            { id: 'manipulation_detector', name: 'Manipulation Detection' },
            { id: 'content_analyzer', name: 'Content Analysis' }
        ];
        
        services.forEach(service => {
            const serviceData = detailed_analysis[service.id];
            if (!serviceData || Object.keys(serviceData).length === 0) return;
            
            // Add page break if needed
            if (yPosition > pageHeight - 80) {
                doc.addPage();
                yPosition = 20;
            }
            
            // Service header with background
            doc.setFillColor(245, 245, 245);
            doc.rect(margin, yPosition - 5, contentWidth, 15, 'F');
            doc.setTextColor(0, 0, 0);
            addText(service.name.toUpperCase(), 14, 'bold');
            yPosition += 10;
            
            // Add meaningful analysis for each service
            this.addServiceAnalysisToPDF(service.id, serviceData, addText);
            
            yPosition += 10;
        });
        
        // Footer on all pages
        const totalPages = doc.internal.getNumberOfPages();
        for (let i = 1; i <= totalPages; i++) {
            doc.setPage(i);
            doc.setFontSize(10);
            doc.setTextColor(128, 128, 128);
            doc.text(
                `Page ${i} of ${totalPages} | Generated by TruthLens AI | ${new Date().toLocaleDateString()}`,
                pageWidth / 2,
                pageHeight - 10,
                { align: 'center' }
            );
        }
    },
    
    addServiceAnalysisToPDF(serviceId, data, addText) {
        switch (serviceId) {
            case 'source_credibility':
                this.addSourceCredibilityToPDF(data, addText);
                break;
                
            case 'author_analyzer':
                this.addAuthorAnalysisToPDF(data, addText);
                break;
                
            case 'bias_detector':
                this.addBiasAnalysisToPDF(data, addText);
                break;
                
            case 'fact_checker':
                this.addFactCheckingToPDF(data, addText);
                break;
                
            case 'transparency_analyzer':
                this.addTransparencyAnalysisToPDF(data, addText);
                break;
                
            case 'manipulation_detector':
                this.addManipulationAnalysisToPDF(data, addText);
                break;
                
            case 'content_analyzer':
                this.addContentAnalysisToPDF(data, addText);
                break;
        }
    },

    addSourceCredibilityToPDF(data, addText) {
        addText('Credibility Assessment:', 12, 'bold');
        addText(`Score: ${data.credibility_score || 0}/100`, 11);
        addText(`Source: ${data.source_name || 'Unknown'}`, 11);
        if (data.domain_age_days) {
            addText(`Domain Age: ${Math.floor(data.domain_age_days / 365)} years`, 11);
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getSourceMeaning(data), 11);
    },
    
    addAuthorAnalysisToPDF(data, addText) {
        addText('Author Profile:', 12, 'bold');
        addText(`Name: ${data.author_name || 'Unknown'}`, 11);
        addText(`Credibility Score: ${data.author_score || 0}`, 11);
        addText(`Verification: ${data.verification_status?.verified ? 'Verified' : 'Unverified'}`, 11);
        
        if (data.professional_info?.years_experience) {
            addText(`Experience: ${data.professional_info.years_experience}+ years`, 11);
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getAuthorMeaning(data), 11);
    },
    
    addBiasAnalysisToPDF(data, addText) {
        const biasScore = data.bias_score || 0;
        addText('Bias Analysis:', 12, 'bold');
        addText(`Bias Score: ${biasScore}%`, 11);
        addText(`Objectivity: ${100 - biasScore}%`, 11);
        
        if (data.loaded_phrases && data.loaded_phrases.length > 0) {
            addText(`Loaded Phrases: ${data.loaded_phrases.length} detected`, 11);
            
            // Add a few examples
            const examples = data.loaded_phrases.slice(0, 3);
            addText('Examples of biased language:', 11, 'bold');
            examples.forEach(phrase => {
                const text = typeof phrase === 'string' ? phrase : phrase.phrase || phrase.text || 'Unknown phrase';
                addText(`• "${text}"`, 11, 'normal', 5);
            });
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getBiasMeaning(data), 11);
    },
    
    addFactCheckingToPDF(data, addText) {
        const checks = data.fact_checks || [];
        const verified = checks.filter(c => c.verdict === 'True' || c.verdict === 'Verified').length;
        
        addText('Fact Checking:', 12, 'bold');
        addText(`Claims Analyzed: ${checks.length}`, 11);
        addText(`Verified: ${verified}`, 11);
        addText(`Accuracy: ${checks.length > 0 ? Math.round((verified/checks.length)*100) : 0}%`, 11);
        
        if (checks.length > 0) {
            addText('Sample Claims:', 11, 'bold');
            checks.slice(0, 3).forEach((check, i) => {
                addText(`${i + 1}. "${check.claim}"`, 11, 'normal', 5);
                addText(`   Verdict: ${check.verdict}`, 11, 'normal', 10);
            });
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getFactCheckingMeaning(data), 11);
    },
    
    addTransparencyAnalysisToPDF(data, addText) {
        addText('Transparency:', 12, 'bold');
        addText(`Score: ${data.transparency_score || 0}%`, 11);
        
        const items = [
            `Sources Cited: ${data.sources_cited ? 'Yes' : 'No'}`,
            `Author Disclosed: ${data.has_author ? 'Yes' : 'No'}`,
            `Direct Quotes: ${data.has_quotes ? 'Yes' : 'No'}`
        ];
        items.forEach(item => addText(`• ${item}`, 11));
        
        addText('What This Means:', 12, 'bold');
        addText(this.getTransparencyMeaning(data), 11);
    },
    
    addManipulationAnalysisToPDF(data, addText) {
        const level = data.manipulation_level || 'Unknown';
        const count = data.techniques?.length || data.tactic_count || 0;
        
        addText('Manipulation Detection:', 12, 'bold');
        addText(`Manipulation Level: ${level}`, 11);
        addText(`Tactics Found: ${count}`, 11);
        
        if (data.techniques && data.techniques.length > 0) {
            addText('Manipulation Techniques Found:', 12, 'bold');
            data.techniques.slice(0, 3).forEach(tech => {
                const name = tech.name || tech.type || tech;
                addText(`• ${name}`, 11);
            });
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getManipulationMeaning(data), 11);
    },
    
    addContentAnalysisToPDF(data, addText) {
        addText('Content Quality:', 12, 'bold');
        if (data.quality_score !== undefined) {
            addText(`Quality Score: ${data.quality_score}/100`, 11);
        }
        if (data.readability?.level) {
            addText(`Reading Level: ${data.readability.level}`, 11);
        }
        if (data.readability?.score !== undefined) {
            addText(`Readability Score: ${data.readability.score}`, 11);
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getContentAnalysisMeaning(data), 11);
    },

    // Helper methods for generating meaningful content
    getFactCheckingMeaning(data) {
        const checks = data.fact_checks || [];
        const total = checks.length;
        const verified = checks.filter(c => c.verdict === 'True' || c.verdict === 'Verified').length;
        
        if (total === 0) {
            return 'No specific factual claims were identified for verification in this article.';
        }
        
        const accuracy = (verified / total) * 100;
        
        if (accuracy >= 80) {
            return `${verified} out of ${total} claims were verified as accurate. The article is well-researched and factually reliable.`;
        } else if (accuracy >= 60) {
            return `${verified} out of ${total} claims were verified. While mostly accurate, some claims lack supporting evidence.`;
        } else if (accuracy >= 40) {
            return `Only ${verified} out of ${total} claims could be verified. Many statements lack supporting evidence or contradict established facts.`;
        } else {
            return `Only ${verified} out of ${total} claims are accurate. This article contains numerous false or misleading statements.`;
        }
    },

    getManipulationMeaning(data) {
        const level = data.manipulation_level || data.level || 'Unknown';
        const count = data.techniques?.length || data.tactic_count || 0;
        
        if (level === 'Low' || level === 'Minimal' || count === 0) {
            return 'This article presents information directly without attempting to manipulate readers. The arguments are logical and evidence-based.';
        } else if (level === 'Moderate' || count <= 3) {
            return `We detected ${count} manipulation techniques. While not severe, these tactics attempt to influence your thinking through emotional appeals rather than facts.`;
        } else {
            return `This article employs ${count} manipulation techniques designed to bypass critical thinking. The content appears designed to persuade through manipulation.`;
        }
    },

    getContentAnalysisMeaning(data) {
        let meaning = '';
        
        if (data.readability?.level) {
            const level = data.readability.level.toLowerCase();
            if (level.includes('college') || level.includes('graduate')) {
                meaning += 'The article uses complex vocabulary typical of academic writing. ';
            } else if (level.includes('high school')) {
                meaning += 'The article is written at an appropriate level for general audiences. ';
            } else {
                meaning += 'The article uses simple language that may oversimplify complex topics. ';
            }
        }
        
        if (data.quality_score !== undefined) {
            if (data.quality_score >= 80) {
                meaning += 'The writing quality is professional with good structure and clarity.';
            } else if (data.quality_score >= 60) {
                meaning += 'The writing quality is acceptable but has room for improvement.';
            } else {
                meaning += 'The writing quality is poor, which may indicate lack of editorial standards.';
            }
        }
        
        return meaning || 'Content analysis helps assess the professionalism and quality of the writing.';
    }
};

// Export for use in main services module
window.TruthLensPDFService = TruthLensPDFService;
