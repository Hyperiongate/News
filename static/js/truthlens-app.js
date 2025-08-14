// truthlens-app.js - Enhanced with meaningful analysis explanations and proper PDF generation
// This file contains the main app class, initialization, and UI functions

// ============================================================================
// SECTION 1: Configuration and Constants
// ============================================================================

// Global state
let currentAnalysis = null;
let isAnalyzing = false;
let charts = {};
let isPro = true; // For development, keep pro features open

// Service definitions
const services = [
    {
        id: 'source_credibility',
        name: 'Source Credibility',
        icon: 'fa-shield-alt',
        description: 'Evaluates the reliability and trustworthiness of the news source',
        isPro: false
    },
    {
        id: 'author_analyzer',
        name: 'Author Analysis',
        icon: 'fa-user-check',
        description: 'Analyzes author credentials and publishing history',
        isPro: false
    },
    {
        id: 'bias_detector',
        name: 'Bias Detection',
        icon: 'fa-balance-scale',
        description: 'Identifies political, ideological, and narrative biases',
        isPro: true
    },
    {
        id: 'fact_checker',
        name: 'Fact Verification',
        icon: 'fa-check-double',
        description: 'Verifies claims against trusted fact-checking databases',
        isPro: true
    },
    {
        id: 'transparency_analyzer',
        name: 'Transparency Analysis',
        icon: 'fa-eye',
        description: 'Evaluates source disclosure and funding transparency',
        isPro: true
    },
    {
        id: 'manipulation_detector',
        name: 'Manipulation Detection',
        icon: 'fa-mask',
        description: 'Detects emotional manipulation and propaganda techniques',
        isPro: true
    },
    {
        id: 'content_analyzer',
        name: 'Content Analysis',
        icon: 'fa-file-alt',
        description: 'Analyzes writing quality, structure, and coherence',
        isPro: true
    }
];

// ============================================================================
// SECTION 2: TruthLensApp Class
// ============================================================================

class TruthLensApp {
    constructor() {
        this.currentAnalysis = null;
        this.isPremium = false;
        this.currentTab = 'url';
        this.API_ENDPOINT = '/api/analyze';
        this.progressInterval = null;
        this.analysisStartTime = null;
        this.analysisComponents = new AnalysisComponents();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSampleData();
        console.log('TruthLens initialized');
    }

    setupEventListeners() {
        // URL input
        const urlInput = document.getElementById('urlInput');
        if (urlInput) {
            urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.analyzeArticle();
                }
            });
        }

        // Text input
        const textInput = document.getElementById('textInput');
        if (textInput) {
            textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.analyzeArticle();
                }
            });
        }

        // Analyze button
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeArticle());
        }

        // Download PDF button
        const downloadBtn = document.getElementById('downloadPdfBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadPDF());
        }

        // Share button
        const shareBtn = document.getElementById('shareResultsBtn');
        if (shareBtn) {
            shareBtn.addEventListener('click', () => this.shareResults());
        }

        // Example buttons for site blocking message
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const url = e.target.getAttribute('data-url');
                if (url && urlInput) {
                    urlInput.value = url;
                    this.analyzeArticle();
                }
            });
        });
    }

    async analyzeArticle() {
        if (isAnalyzing) return;

        const urlInput = document.getElementById('urlInput');
        const textInput = document.getElementById('textInput');
        
        let input;
        let inputType;

        if (this.currentTab === 'url') {
            input = urlInput?.value?.trim();
            inputType = 'url';
            if (!input) {
                this.showError('Please enter a URL to analyze');
                return;
            }
        } else {
            input = textInput?.value?.trim();
            inputType = 'text';
            if (!input) {
                this.showError('Please enter text to analyze');
                return;
            }
        }

        isAnalyzing = true;
        this.analysisStartTime = Date.now();
        this.showLoading();
        this.resetProgress();
        this.startProgressAnimation();

        try {
            const payload = inputType === 'url' ? { url: input } : { text: input };
            payload.is_pro = isPro;

            const response = await fetch(this.API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || `Server error: ${response.status}`);
            }

            // Store the analysis
            this.currentAnalysis = currentAnalysis = data;
            window.currentAnalysis = data; // For global access

            // Complete progress and show results
            this.completeProgress();
            setTimeout(() => {
                this.hideLoading();
                this.displayResults(data);
            }, 1000);

        } catch (error) {
            console.error('Analysis error:', error);
            this.hideLoading();
            
            // Check if it's a site blocking error
            if (error.message && error.message.includes('blocked')) {
                this.showError('It looks like this site is blocking automated analysis. Please use the text option above and copy/paste the entire article to have it analyzed.');
            } else {
                this.showError(`Analysis failed: ${error.message}`);
            }
        } finally {
            isAnalyzing = false;
            this.stopProgressAnimation();
        }
    }

    displayResults(data) {
        const resultsSection = document.getElementById('resultsSection');
        if (!resultsSection) return;

        resultsSection.style.display = 'block';
        
        // Display enhanced trust score with explanation
        this.displayEnhancedTrustScore(data.analysis, data);
        
        // Display meaningful key findings
        this.displayMeaningfulKeyFindings(data);
        
        // Display article info
        if (data.article) {
            this.displayArticleInfo(data.article, data.analysis);
        }
        
        // Display service accordion with enhanced content
        this.displayEnhancedServiceAccordion(data);
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    displayEnhancedTrustScore(analysis, fullData) {
        const score = analysis.trust_score || 0;
        const level = analysis.trust_level || 'Unknown';
        
        // Update score with animation
        this.animateTrustScore(score);
        
        // Update level indicator
        this.updateTrustLevelIndicator(score, level);
        
        // Create trust gauge visualization
        this.analysisComponents.createTrustScoreGauge('trustGauge', score);
        
        // Update summary with detailed explanation
        const summaryEl = document.getElementById('trustSummary');
        summaryEl.innerHTML = this.getTrustSummaryExplanation(score, level, fullData);
        
        // Display trust breakdown with explanations
        this.displayTrustBreakdown(fullData.detailed_analysis || {});
    }

    getTrustSummaryExplanation(score, level, data) {
        let explanation = '';
        const servicesUsed = data.services_used || [];
        
        if (score >= 80) {
            explanation = `<strong>High Credibility:</strong> This article demonstrates exceptional journalistic standards. `;
            explanation += `Our analysis of ${servicesUsed.length} key factors including source reputation, author credentials, and factual accuracy indicates this is a highly reliable source of information.`;
        } else if (score >= 60) {
            explanation = `<strong>Moderate Credibility:</strong> This article shows reasonable journalistic standards with some areas of concern. `;
            explanation += `While the source is generally reputable, our analysis identified some issues that warrant careful consideration of the claims made.`;
        } else if (score >= 40) {
            explanation = `<strong>Low Credibility:</strong> This article has significant credibility issues. `;
            explanation += `Multiple red flags were identified including potential bias, unverified claims, or questionable sourcing. Verify information through additional sources.`;
        } else {
            explanation = `<strong>Very Low Credibility:</strong> This article fails to meet basic journalistic standards. `;
            explanation += `Major concerns were identified across multiple dimensions. Exercise extreme caution and seek alternative sources for any claims made.`;
        }
        
        return explanation;
    }

    displayMeaningfulKeyFindings(data) {
        const findingsContainer = document.getElementById('keyFindings');
        if (!findingsContainer) return;

        const findings = this.generateMeaningfulFindings(data);
        
        if (findings.length > 0) {
            let findingsHtml = '';
            findings.forEach(finding => {
                const icon = finding.type === 'positive' ? 'fa-check-circle' : 
                           finding.type === 'negative' ? 'fa-times-circle' : 'fa-exclamation-circle';
                
                findingsHtml += `
                    <div class="finding-item finding-${finding.type}">
                        <i class="fas ${icon}"></i>
                        <div class="finding-content">
                            <strong>${finding.title}:</strong> ${finding.explanation}
                        </div>
                    </div>
                `;
            });
            findingsContainer.innerHTML = findingsHtml;
        } else {
            findingsContainer.innerHTML = `
                <div class="info-box">
                    <div class="info-box-title">
                        <i class="fas fa-info-circle"></i>
                        Analysis Complete
                    </div>
                    <div class="info-box-content">
                        We've completed a comprehensive analysis of this article. Review the detailed findings below to understand the credibility assessment.
                    </div>
                </div>
            `;
        }
    }

    generateMeaningfulFindings(data) {
        const findings = [];
        const analysis = data.detailed_analysis || {};
        
        // Source credibility finding
        if (analysis.source_credibility) {
            const score = analysis.source_credibility.credibility_score || 0;
            if (score >= 80) {
                findings.push({
                    type: 'positive',
                    title: 'Highly Reputable Source',
                    explanation: `${analysis.source_credibility.source_name || 'This source'} is a well-established news outlet with strong editorial standards and fact-checking practices.`
                });
            } else if (score < 50) {
                findings.push({
                    type: 'negative',
                    title: 'Source Credibility Concerns',
                    explanation: `This source has limited credibility indicators. It may lack editorial oversight, transparency, or has a history of publishing unverified information.`
                });
            }
        }

        // Author credibility finding
        if (analysis.author_analyzer) {
            const authorData = analysis.author_analyzer;
            if (authorData.verified && authorData.years_experience > 5) {
                findings.push({
                    type: 'positive',
                    title: 'Experienced Journalist',
                    explanation: `Author ${authorData.author_name || 'The author'} has ${authorData.years_experience} years of experience and a verified track record in journalism.`
                });
            } else if (!authorData.found || authorData.credibility_score < 50) {
                findings.push({
                    type: 'warning',
                    title: 'Limited Author Information',
                    explanation: 'Unable to verify the author\'s credentials or journalism experience. This may indicate less editorial oversight.'
                });
            }
        }

        // Bias detection finding
        if (analysis.bias_detector) {
            const biasScore = analysis.bias_detector.overall_bias_score || 0;
            if (biasScore > 70) {
                findings.push({
                    type: 'negative',
                    title: 'High Bias Detected',
                    explanation: `This article shows significant bias indicators including loaded language, one-sided arguments, and potential agenda-driven reporting.`
                });
            } else if (biasScore < 30) {
                findings.push({
                    type: 'positive',
                    title: 'Balanced Reporting',
                    explanation: 'The article maintains objectivity with balanced perspectives and neutral language.'
                });
            }
        }

        // Fact checking finding
        if (analysis.fact_checker && analysis.fact_checker.claims_checked > 0) {
            const verified = analysis.fact_checker.verified_count || 0;
            const total = analysis.fact_checker.claims_checked;
            const percentage = (verified / total * 100).toFixed(0);
            
            if (percentage >= 80) {
                findings.push({
                    type: 'positive',
                    title: 'Facts Verified',
                    explanation: `${percentage}% of checkable claims (${verified}/${total}) were verified through independent fact-checking sources.`
                });
            } else if (percentage < 50) {
                findings.push({
                    type: 'negative',
                    title: 'Unverified Claims',
                    explanation: `Only ${percentage}% of claims could be verified. Multiple statements lack supporting evidence or contradict established facts.`
                });
            }
        }

        // Sort by severity
        return findings.sort((a, b) => {
            const order = { negative: 0, warning: 1, positive: 2 };
            return order[a.type] - order[b.type];
        });
    }

    displayTrustBreakdown(detailedAnalysis) {
        const components = [
            {
                name: 'Source Reputation',
                score: this.extractScore(detailedAnalysis.source_credibility, ['credibility_score', 'score']),
                whatWeChecked: 'Domain age, SSL certificates, editorial standards, correction policies, and industry reputation.',
                whatWeFound: this.getSourceFindings(detailedAnalysis.source_credibility),
                whatThisMeans: this.getSourceMeaning(detailedAnalysis.source_credibility)
            },
            {
                name: 'Author Credibility',
                score: this.extractScore(detailedAnalysis.author_analyzer, ['credibility_score', 'score']),
                whatWeChecked: 'Author identity verification, publishing history, expertise areas, and professional affiliations.',
                whatWeFound: this.getAuthorFindings(detailedAnalysis.author_analyzer),
                whatThisMeans: this.getAuthorMeaning(detailedAnalysis.author_analyzer)
            },
            {
                name: 'Transparency',
                score: this.extractScore(detailedAnalysis.transparency_analyzer, ['transparency_score', 'score']),
                whatWeChecked: 'Source citations, funding disclosures, conflict of interest statements, and correction policies.',
                whatWeFound: this.getTransparencyFindings(detailedAnalysis.transparency_analyzer),
                whatThisMeans: this.getTransparencyMeaning(detailedAnalysis.transparency_analyzer)
            },
            {
                name: 'Objectivity',
                score: detailedAnalysis.bias_detector ? 
                    (100 - (detailedAnalysis.bias_detector.overall_bias_score || 0)) : 50,
                whatWeChecked: 'Language analysis for loaded terms, source diversity, perspective balance, and emotional manipulation.',
                whatWeFound: this.getBiasFindings(detailedAnalysis.bias_detector),
                whatThisMeans: this.getBiasMeaning(detailedAnalysis.bias_detector)
            }
        ];

        const container = document.querySelector('.trust-breakdown');
        if (container) {
            container.innerHTML = components.map(comp => `
                <div class="trust-component">
                    <div class="component-header">
                        <h4>${comp.name}</h4>
                        <div class="component-score ${this.getScoreClass(comp.score)}">
                            ${comp.score}%
                        </div>
                    </div>
                    <div class="component-analysis">
                        <div class="analysis-section">
                            <div class="analysis-section-title">
                                <i class="fas fa-search"></i>
                                What We Checked
                            </div>
                            <div class="analysis-section-content">
                                ${comp.whatWeChecked}
                            </div>
                        </div>
                        <div class="analysis-section">
                            <div class="analysis-section-title">
                                <i class="fas fa-clipboard-list"></i>
                                What We Found
                            </div>
                            <div class="analysis-section-content">
                                ${comp.whatWeFound}
                            </div>
                        </div>
                        <div class="analysis-section">
                            <div class="analysis-section-title">
                                <i class="fas fa-lightbulb"></i>
                                What This Means
                            </div>
                            <div class="analysis-section-content">
                                ${comp.whatThisMeans}
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    }

    // Helper methods for generating meaningful explanations
    getSourceFindings(data) {
        if (!data) return 'Unable to analyze source credibility.';
        
        const findings = [];
        
        if (data.domain_age_days > 365) {
            findings.push(`Established domain (${Math.floor(data.domain_age_days / 365)} years old)`);
        } else if (data.domain_age_days > 0) {
            findings.push(`Relatively new domain (${data.domain_age_days} days old)`);
        }
        
        if (data.has_ssl) {
            findings.push('Secure connection verified');
        }
        
        if (data.credibility_indicators) {
            const indicators = data.credibility_indicators;
            if (indicators.has_about_page) findings.push('Has About page');
            if (indicators.has_contact_info) findings.push('Contact information available');
            if (indicators.has_editorial_policy) findings.push('Editorial policy published');
        }
        
        return findings.length > 0 ? findings.join(', ') + '.' : 'Limited credibility indicators found.';
    }

    getSourceMeaning(data) {
        if (!data) return 'Source credibility could not be determined.';
        
        const score = data.credibility_score || 0;
        if (score >= 80) {
            return 'This is a highly credible news source with established journalistic standards and transparency.';
        } else if (score >= 60) {
            return 'This source shows reasonable credibility but may lack some transparency or editorial standards.';
        } else if (score >= 40) {
            return 'This source has limited credibility indicators. Verify information through additional sources.';
        } else {
            return 'This source lacks basic credibility indicators. Exercise caution with any claims made.';
        }
    }

    getAuthorFindings(data) {
        if (!data) return 'No author information available.';
        
        const findings = [];
        
        if (data.author_name) {
            findings.push(`Author: ${data.author_name}`);
        }
        
        if (data.verified) {
            findings.push('Identity verified');
        }
        
        if (data.years_experience > 0) {
            findings.push(`${data.years_experience} years of journalism experience`);
        }
        
        if (data.total_articles > 0) {
            findings.push(`${data.total_articles} published articles found`);
        }
        
        if (data.expertise_areas && data.expertise_areas.length > 0) {
            findings.push(`Expertise in: ${data.expertise_areas.slice(0, 3).join(', ')}`);
        }
        
        return findings.length > 0 ? findings.join(', ') + '.' : 'Unable to verify author credentials.';
    }

    getAuthorMeaning(data) {
        if (!data || !data.found) {
            return 'Without verified author information, the credibility of this article cannot be fully assessed.';
        }
        
        const score = data.credibility_score || 0;
        if (score >= 80) {
            return 'The author is a verified journalist with extensive experience and a strong track record.';
        } else if (score >= 60) {
            return 'The author has some journalism experience but limited verification available.';
        } else if (score >= 40) {
            return 'Limited information about the author raises questions about editorial oversight.';
        } else {
            return 'Lack of author transparency is a significant credibility concern.';
        }
    }

    getTransparencyFindings(data) {
        if (!data) return 'Transparency analysis not available.';
        
        const findings = [];
        
        if (data.has_sources) findings.push('Sources cited');
        if (data.has_disclosure) findings.push('Disclosure statement present');
        if (data.has_corrections) findings.push('Corrections policy available');
        if (data.has_funding_info) findings.push('Funding information disclosed');
        
        const score = data.transparency_score || 0;
        findings.push(`Overall transparency: ${score}%`);
        
        return findings.join(', ') + '.';
    }

    getTransparencyMeaning(data) {
        if (!data) return 'Transparency level could not be determined.';
        
        const score = data.transparency_score || 0;
        if (score >= 80) {
            return 'Excellent transparency with clear sourcing, disclosures, and accountability measures.';
        } else if (score >= 60) {
            return 'Good transparency but missing some key elements like funding disclosure or correction policies.';
        } else {
            return 'Limited transparency raises questions about potential conflicts of interest or hidden agendas.';
        }
    }

    getBiasFindings(data) {
        if (!data) return 'Bias analysis not available.';
        
        const findings = [];
        
        if (data.political_lean !== undefined) {
            const lean = data.political_lean;
            if (Math.abs(lean) < 10) {
                findings.push('Politically neutral');
            } else if (lean < -10) {
                findings.push(`Left-leaning (${Math.abs(lean)}% bias)`);
            } else if (lean > 10) {
                findings.push(`Right-leaning (${lean}% bias)`);
            }
        }
        
        if (data.loaded_phrases && data.loaded_phrases.length > 0) {
            findings.push(`${data.loaded_phrases.length} loaded phrases detected`);
        }
        
        if (data.manipulation_tactics && data.manipulation_tactics.length > 0) {
            findings.push('Manipulation tactics identified');
        }
        
        return findings.length > 0 ? findings.join(', ') + '.' : 'No significant bias indicators found.';
    }

    getBiasMeaning(data) {
        if (!data) return 'Bias level could not be determined.';
        
        const biasScore = data.overall_bias_score || 0;
        if (biasScore < 30) {
            return 'The article maintains objectivity and presents balanced perspectives without significant bias.';
        } else if (biasScore < 60) {
            return 'Some bias is present but within acceptable journalistic standards. Be aware of the perspective.';
        } else {
            return 'Significant bias detected. This article presents a one-sided view and should be balanced with other sources.';
        }
    }

    displayEnhancedServiceAccordion(data) {
        const container = document.getElementById('servicesAccordion');
        if (!container) return;
        
        container.innerHTML = '';
        const servicesData = data.detailed_analysis || {};
        
        services.forEach((service, index) => {
            const serviceData = servicesData[service.id] || {};
            const accordionItem = this.createEnhancedServiceAccordionItem(service, serviceData, index);
            container.appendChild(accordionItem);
        });
    }

    createEnhancedServiceAccordionItem(service, serviceData, index) {
        const item = document.createElement('div');
        item.className = 'service-accordion-item';
        item.id = `service-${service.id}`;
        
        const hasData = serviceData && Object.keys(serviceData).length > 0;
        const expandedContent = this.getEnhancedServiceContent(service.id, serviceData);
        
        item.innerHTML = `
            <div class="service-accordion-header" onclick="window.truthLensApp.toggleAccordion('${service.id}')">
                <div class="service-header-content">
                    <div class="service-icon-wrapper">
                        <i class="fas ${service.icon}"></i>
                    </div>
                    <div class="service-info">
                        <h3 class="service-name">${service.name}</h3>
                        <p class="service-description">${service.description}</p>
                        ${hasData ? this.getServicePreviewHTML(service.id, serviceData) : 
                            '<div class="service-preview"><span class="preview-value" style="color: #6b7280">Analysis not available</span></div>'}
                    </div>
                </div>
                ${service.isPro && !isPro ? 
                    '<div class="pro-badge"><i class="fas fa-crown"></i> Pro</div>' : 
                    '<i class="fas fa-chevron-down service-expand-icon"></i>'}
            </div>
            <div class="service-accordion-content">
                <div class="service-content-inner">
                    ${expandedContent}
                </div>
            </div>
        `;
        
        return item;
    }

    getServicePreviewHTML(serviceId, data) {
        const previewData = this.getServicePreviewData(serviceId, data);
        return `
            <div class="service-preview">
                ${previewData.map(preview => `
                    <div class="preview-item">
                        <span class="preview-label">${preview.label}:</span>
                        <span class="preview-value" style="color: ${preview.color || 'inherit'}">
                            ${preview.value}
                        </span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    getServicePreviewData(serviceId, data) {
        if (!data || Object.keys(data).length === 0) {
            return [{ label: 'Status', value: 'Not Available', color: '#6b7280' }];
        }
        
        switch (serviceId) {
            case 'source_credibility':
                const sourceScore = data.credibility_score || 0;
                return [
                    { label: 'Score', value: `${sourceScore}/100`, color: this.getScoreColor(sourceScore) },
                    { label: 'Level', value: data.credibility_level || 'Unknown' }
                ];
                
            case 'author_analyzer':
                const authorScore = data.credibility_score || 0;
                return [
                    { label: 'Author', value: data.author_name || 'Unknown' },
                    { label: 'Score', value: `${authorScore}/100`, color: this.getScoreColor(authorScore) }
                ];
                
            case 'bias_detector':
                const biasScore = data.overall_bias_score || 0;
                const objectivity = 100 - biasScore;
                return [
                    { label: 'Bias Level', value: data.bias_level || 'Unknown' },
                    { label: 'Objectivity', value: `${objectivity}%`, color: this.getScoreColor(objectivity) }
                ];
                
            case 'fact_checker':
                const verified = data.verified_count || 0;
                const total = data.claims_checked || 0;
                const accuracy = total > 0 ? Math.round((verified / total) * 100) : 0;
                return [
                    { label: 'Claims Checked', value: total },
                    { label: 'Accuracy', value: `${accuracy}%`, color: this.getScoreColor(accuracy) }
                ];
                
            case 'transparency_analyzer':
                const transScore = data.transparency_score || 0;
                return [
                    { label: 'Score', value: `${transScore}/100`, color: this.getScoreColor(transScore) },
                    { label: 'Sources', value: data.has_sources ? 'Cited' : 'Missing' }
                ];
                
            case 'manipulation_detector':
                const manipulationDetected = data.manipulation_detected || false;
                return [
                    { label: 'Status', value: manipulationDetected ? 'Detected' : 'Clean', 
                      color: manipulationDetected ? '#ef4444' : '#10b981' }
                ];
                
            case 'content_analyzer':
                const readingLevel = data.reading_level || 'Unknown';
                return [
                    { label: 'Reading Level', value: readingLevel },
                    { label: 'Quality', value: data.quality_score ? `${data.quality_score}%` : 'N/A' }
                ];
                
            default:
                return [{ label: 'Status', value: 'Analysis Complete' }];
        }
    }

    getEnhancedServiceContent(serviceId, data) {
        if (!data || Object.keys(data).length === 0) {
            return '<div class="no-data-message">This analysis is not available for the current article.</div>';
        }
        
        switch (serviceId) {
            case 'source_credibility':
                return this.getSourceCredibilityContent(data);
            case 'author_analyzer':
                return this.getAuthorAnalysisContent(data);
            case 'bias_detector':
                return this.getBiasDetectionContent(data);
            case 'fact_checker':
                return this.getFactCheckerContent(data);
            case 'transparency_analyzer':
                return this.getTransparencyContent(data);
            case 'manipulation_detector':
                return this.getManipulationContent(data);
            case 'content_analyzer':
                return this.getContentAnalysisContent(data);
            default:
                return '<div class="no-data-message">Analysis details unavailable.</div>';
        }
    }

    getSourceCredibilityContent(data) {
        return `
            <div class="service-analysis-structure">
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-search"></i>
                        What We Analyzed
                    </div>
                    <div class="analysis-section-content">
                        We examined ${data.source_name || 'this source'} across multiple credibility dimensions including domain registration, 
                        SSL security, editorial standards, correction policies, and industry reputation. We also checked for 
                        state media affiliations and known misinformation patterns.
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-clipboard-list"></i>
                        Key Findings
                    </div>
                    <div class="analysis-section-content">
                        <div class="findings-grid">
                            ${this.renderSourceCredibilityFindings(data)}
                        </div>
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-chart-line"></i>
                        Credibility Score Breakdown
                    </div>
                    <div class="analysis-section-content">
                        <canvas id="sourceCredChart" width="300" height="200"></canvas>
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-lightbulb"></i>
                        What This Means For You
                    </div>
                    <div class="analysis-section-content">
                        ${this.getSourceCredibilityMeaning(data)}
                    </div>
                </div>
            </div>
        `;
    }

    renderSourceCredibilityFindings(data) {
        const findings = [];
        
        if (data.domain_age_days !== undefined) {
            const years = Math.floor(data.domain_age_days / 365);
            const ageText = years > 0 ? `${years} years` : `${data.domain_age_days} days`;
            findings.push(`<div class="finding-item"><strong>Domain Age:</strong> ${ageText}</div>`);
        }
        
        if (data.has_ssl !== undefined) {
            findings.push(`<div class="finding-item"><strong>Security:</strong> ${data.has_ssl ? 'SSL Verified ✓' : 'No SSL ✗'}</div>`);
        }
        
        if (data.credibility_indicators) {
            const indicators = data.credibility_indicators;
            if (indicators.has_about_page !== undefined) {
                findings.push(`<div class="finding-item"><strong>About Page:</strong> ${indicators.has_about_page ? 'Present ✓' : 'Missing ✗'}</div>`);
            }
            if (indicators.has_editorial_policy !== undefined) {
                findings.push(`<div class="finding-item"><strong>Editorial Policy:</strong> ${indicators.has_editorial_policy ? 'Published ✓' : 'Not Found ✗'}</div>`);
            }
        }
        
        if (data.is_satire) {
            findings.push(`<div class="finding-item warning"><strong>⚠ Satire Site Detected</strong></div>`);
        }
        
        if (data.is_state_media) {
            findings.push(`<div class="finding-item warning"><strong>⚠ State Media Affiliation</strong></div>`);
        }
        
        return findings.join('');
    }

    getSourceCredibilityMeaning(data) {
        const score = data.credibility_score || 0;
        let meaning = '';
        
        if (score >= 80) {
            meaning = 'This is a highly reputable news source with strong credibility indicators. You can generally trust information from this outlet, though always remain critical of individual claims.';
        } else if (score >= 60) {
            meaning = 'This source shows decent credibility but has some gaps in transparency or editorial standards. Cross-reference important claims with other sources.';
        } else if (score >= 40) {
            meaning = 'This source has limited credibility indicators. Be cautious and verify all claims through multiple independent sources.';
        } else {
            meaning = 'This source lacks basic credibility markers. Information should be treated with extreme skepticism and verified elsewhere.';
        }
        
        if (data.is_satire) {
            meaning += ' <strong>Note:</strong> This is a satire site intended for entertainment, not factual news.';
        }
        
        if (data.is_state_media) {
            meaning += ' <strong>Note:</strong> This outlet has state media affiliations which may influence editorial independence.';
        }
        
        return meaning;
    }

    getAuthorAnalysisContent(data) {
        return `
            <div class="service-analysis-structure">
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-search"></i>
                        What We Analyzed
                    </div>
                    <div class="analysis-section-content">
                        We searched for ${data.author_name || 'the author'} across journalism databases, news archives, and professional networks. 
                        We analyzed their publishing history, areas of expertise, and professional credentials.
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-user-circle"></i>
                        Author Profile
                    </div>
                    <div class="analysis-section-content">
                        ${this.renderAuthorProfile(data)}
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-chart-bar"></i>
                        Publishing History
                    </div>
                    <div class="analysis-section-content">
                        <canvas id="authorHistoryChart" width="300" height="200"></canvas>
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-lightbulb"></i>
                        What This Means For You
                    </div>
                    <div class="analysis-section-content">
                        ${this.getAuthorAnalysisMeaning(data)}
                    </div>
                </div>
            </div>
        `;
    }

    renderAuthorProfile(data) {
        let profile = '<div class="author-profile">';
        
        profile += `<div class="profile-item"><strong>Name:</strong> ${data.author_name || 'Unknown'}</div>`;
        
        if (data.verified !== undefined) {
            profile += `<div class="profile-item"><strong>Verification:</strong> ${data.verified ? 'Verified Journalist ✓' : 'Unverified'}</div>`;
        }
        
        if (data.years_experience !== undefined) {
            profile += `<div class="profile-item"><strong>Experience:</strong> ${data.years_experience} years</div>`;
        }
        
        if (data.total_articles !== undefined) {
            profile += `<div class="profile-item"><strong>Articles Published:</strong> ${data.total_articles}</div>`;
        }
        
        if (data.expertise_areas && data.expertise_areas.length > 0) {
            profile += `<div class="profile-item"><strong>Expertise Areas:</strong> ${data.expertise_areas.join(', ')}</div>`;
        }
        
        if (data.publications && data.publications.length > 0) {
            profile += `<div class="profile-item"><strong>Publications:</strong> ${data.publications.slice(0, 5).join(', ')}</div>`;
        }
        
        profile += '</div>';
        return profile;
    }

    getAuthorAnalysisMeaning(data) {
        if (!data.found) {
            return 'We could not find information about this author in our journalism databases. This could mean they are new to journalism, write under a pseudonym, or may not be a professional journalist. Without author credentials, it\'s harder to assess the reliability of the reporting.';
        }
        
        const score = data.credibility_score || 0;
        let meaning = '';
        
        if (score >= 80) {
            meaning = `${data.author_name} is an established journalist with ${data.years_experience || 'several'} years of experience. Their track record suggests reliable and professional reporting.`;
        } else if (score >= 60) {
            meaning = `${data.author_name} has some journalism experience but limited public track record. Their reporting should be reliable but verify important claims.`;
        } else if (score >= 40) {
            meaning = `Limited information is available about ${data.author_name}'s journalism background. Exercise caution and cross-reference claims.`;
        } else {
            meaning = `We found very little professional journalism history for ${data.author_name}. This raises questions about editorial oversight and fact-checking.`;
        }
        
        return meaning;
    }

    getBiasDetectionContent(data) {
        return `
            <div class="service-analysis-structure">
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-search"></i>
                        What We Analyzed
                    </div>
                    <div class="analysis-section-content">
                        We performed deep linguistic analysis examining word choice, framing techniques, source selection, 
                        and emotional language. We checked for political bias, corporate influence, sensationalism, 
                        and propaganda techniques across ${data.sentences_analyzed || 'multiple'} sentences.
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-chart-radar"></i>
                        Bias Dimensions
                    </div>
                    <div class="analysis-section-content">
                        <canvas id="biasRadarChart" width="300" height="300"></canvas>
                    </div>
                </div>

                ${data.loaded_phrases && data.loaded_phrases.length > 0 ? `
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-exclamation-triangle"></i>
                        Loaded Language Detected
                    </div>
                    <div class="analysis-section-content">
                        ${this.renderLoadedPhrases(data.loaded_phrases)}
                    </div>
                </div>
                ` : ''}

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-lightbulb"></i>
                        What This Means For You
                    </div>
                    <div class="analysis-section-content">
                        ${this.getBiasDetectionMeaning(data)}
                    </div>
                </div>
            </div>
        `;
    }

    renderLoadedPhrases(phrases) {
        return phrases.slice(0, 5).map(phrase => `
            <div class="loaded-phrase">
                <span class="phrase-text">"${phrase.phrase}"</span>
                <span class="phrase-severity severity-${phrase.severity || 'medium'}">${phrase.type || 'Biased Language'}</span>
            </div>
        `).join('');
    }

    getBiasDetectionMeaning(data) {
        const biasScore = data.overall_bias_score || 0;
        let meaning = '';
        
        if (biasScore < 30) {
            meaning = 'This article demonstrates strong objectivity with minimal bias. The language is neutral and perspectives are balanced.';
        } else if (biasScore < 60) {
            meaning = 'Moderate bias is present in the language and framing. While not severely slanted, be aware of the perspective being promoted.';
        } else {
            meaning = 'Significant bias detected throughout the article. The language is loaded and perspectives are one-sided. Seek alternative viewpoints.';
        }
        
        if (data.political_lean !== undefined) {
            const lean = data.political_lean;
            if (Math.abs(lean) > 20) {
                meaning += ` The article shows a ${lean > 0 ? 'right' : 'left'}-leaning political bias.`;
            }
        }
        
        if (data.manipulation_tactics && data.manipulation_tactics.length > 0) {
            meaning += ' Warning: Emotional manipulation tactics were detected.';
        }
        
        return meaning;
    }

    getFactCheckerContent(data) {
        const total = data.claims_checked || 0;
        const verified = data.verified_count || 0;
        
        return `
            <div class="service-analysis-structure">
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-search"></i>
                        What We Analyzed
                    </div>
                    <div class="analysis-section-content">
                        We identified ${total} checkable claims in this article and verified them against fact-checking databases, 
                        official sources, and scientific literature. Each claim was evaluated for accuracy and supporting evidence.
                    </div>
                </div>

                ${data.claims && data.claims.length > 0 ? `
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-list-check"></i>
                        Fact Check Results
                    </div>
                    <div class="analysis-section-content">
                        ${this.renderFactCheckResults(data.claims)}
                    </div>
                </div>
                ` : ''}

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-chart-pie"></i>
                        Accuracy Summary
                    </div>
                    <div class="analysis-section-content">
                        <canvas id="factCheckPieChart" width="300" height="300"></canvas>
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-lightbulb"></i>
                        What This Means For You
                    </div>
                    <div class="analysis-section-content">
                        ${this.getFactCheckerMeaning(data)}
                    </div>
                </div>
            </div>
        `;
    }

    renderFactCheckResults(claims) {
        return claims.slice(0, 5).map(claim => {
            const verdictClass = claim.verdict === 'True' ? 'verified' : 
                               claim.verdict === 'False' ? 'false' : 'unverified';
            const icon = claim.verdict === 'True' ? 'fa-check' : 
                        claim.verdict === 'False' ? 'fa-times' : 'fa-question';
            
            return `
                <div class="fact-check-item">
                    <div class="claim-text">"${claim.claim}"</div>
                    <div class="claim-verdict ${verdictClass}">
                        <i class="fas ${icon}"></i> ${claim.verdict}
                    </div>
                    ${claim.explanation ? `<div class="claim-explanation">${claim.explanation}</div>` : ''}
                </div>
            `;
        }).join('');
    }

    getFactCheckerMeaning(data) {
        const total = data.claims_checked || 0;
        const verified = data.verified_count || 0;
        
        if (total === 0) {
            return 'No specific factual claims were identified for verification in this article.';
        }
        
        const accuracy = (verified / total) * 100;
        let meaning = '';
        
        if (accuracy >= 80) {
            meaning = `Excellent factual accuracy with ${verified} out of ${total} claims verified. The article is well-researched and factually reliable.`;
        } else if (accuracy >= 60) {
            meaning = `Good factual accuracy with ${verified} out of ${total} claims verified. Most information is accurate but some claims need verification.`;
        } else if (accuracy >= 40) {
            meaning = `Moderate accuracy with only ${verified} out of ${total} claims verified. Many statements lack supporting evidence.`;
        } else {
            meaning = `Poor factual accuracy with only ${verified} out of ${total} claims verified. Most claims are unsubstantiated or false.`;
        }
        
        return meaning;
    }

    getTransparencyContent(data) {
        return `
            <div class="service-analysis-structure">
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-search"></i>
                        What We Analyzed
                    </div>
                    <div class="analysis-section-content">
                        We examined the article for transparency indicators including source citations, author disclosure, 
                        funding information, and conflict of interest statements. Transparency is crucial for assessing 
                        potential biases and agendas.
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-clipboard-check"></i>
                        Transparency Checklist
                    </div>
                    <div class="analysis-section-content">
                        ${this.renderTransparencyChecklist(data)}
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-lightbulb"></i>
                        What This Means For You
                    </div>
                    <div class="analysis-section-content">
                        ${this.getTransparencyMeaning(data)}
                    </div>
                </div>
            </div>
        `;
    }

    renderTransparencyChecklist(data) {
        const items = [
            { label: 'Sources Cited', value: data.has_sources, key: 'sources' },
            { label: 'Author Disclosed', value: data.has_author, key: 'author' },
            { label: 'Date Published', value: data.has_date, key: 'date' },
            { label: 'Funding Disclosed', value: data.has_funding_info, key: 'funding' },
            { label: 'Conflicts Disclosed', value: data.has_disclosure, key: 'disclosure' },
            { label: 'Corrections Policy', value: data.has_corrections, key: 'corrections' }
        ];
        
        return `
            <div class="transparency-checklist">
                ${items.map(item => `
                    <div class="checklist-item">
                        <span class="checklist-label">${item.label}</span>
                        <span class="checklist-value ${item.value ? 'present' : 'missing'}">
                            ${item.value ? '<i class="fas fa-check"></i> Present' : '<i class="fas fa-times"></i> Missing'}
                        </span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    getManipulationContent(data) {
        return `
            <div class="service-analysis-structure">
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-search"></i>
                        What We Analyzed
                    </div>
                    <div class="analysis-section-content">
                        We scanned for propaganda techniques, emotional manipulation, logical fallacies, and psychological tactics 
                        designed to bypass critical thinking. This includes fear-mongering, false dichotomies, and appeal to emotions.
                    </div>
                </div>

                ${data.techniques_found && data.techniques_found.length > 0 ? `
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-exclamation-triangle"></i>
                        Manipulation Techniques Detected
                    </div>
                    <div class="analysis-section-content">
                        ${this.renderManipulationTechniques(data.techniques_found)}
                    </div>
                </div>
                ` : ''}

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-lightbulb"></i>
                        What This Means For You
                    </div>
                    <div class="analysis-section-content">
                        ${this.getManipulationMeaning(data)}
                    </div>
                </div>
            </div>
        `;
    }

    renderManipulationTechniques(techniques) {
        return techniques.map(tech => `
            <div class="manipulation-technique">
                <div class="technique-name">${tech.name}</div>
                <div class="technique-description">${tech.description}</div>
                <div class="technique-severity severity-${tech.severity || 'medium'}">
                    ${tech.severity || 'Medium'} Impact
                </div>
            </div>
        `).join('');
    }

    getManipulationMeaning(data) {
        if (!data.manipulation_detected) {
            return 'No significant manipulation tactics were detected. The article appears to present information straightforwardly without attempting to manipulate readers\' emotions or bypass critical thinking.';
        }
        
        const count = data.techniques_found ? data.techniques_found.length : 0;
        return `We detected ${count} manipulation technique${count !== 1 ? 's' : ''} in this article. These tactics are designed to influence your thinking through emotional appeal rather than factual argument. Read critically and focus on verifiable facts rather than emotional rhetoric.`;
    }

    getContentAnalysisContent(data) {
        return `
            <div class="service-analysis-structure">
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-search"></i>
                        What We Analyzed
                    </div>
                    <div class="analysis-section-content">
                        We evaluated the writing quality, readability, structure, and professionalism of the content. 
                        This includes grammar, coherence, evidence quality, and whether the content appears to be 
                        AI-generated or plagiarized.
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-chart-bar"></i>
                        Content Metrics
                    </div>
                    <div class="analysis-section-content">
                        ${this.renderContentMetrics(data)}
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-lightbulb"></i>
                        What This Means For You
                    </div>
                    <div class="analysis-section-content">
                        ${this.getContentAnalysisMeaning(data)}
                    </div>
                </div>
            </div>
        `;
    }

    renderContentMetrics(data) {
        const metrics = [];
        
        if (data.reading_level) {
            metrics.push(`<div class="metric-item"><strong>Reading Level:</strong> ${data.reading_level}</div>`);
        }
        
        if (data.flesch_score !== undefined) {
            const difficulty = data.flesch_score > 60 ? 'Easy' : 
                             data.flesch_score > 30 ? 'Moderate' : 'Difficult';
            metrics.push(`<div class="metric-item"><strong>Readability:</strong> ${difficulty} (Flesch: ${data.flesch_score})</div>`);
        }
        
        if (data.sentence_count !== undefined) {
            metrics.push(`<div class="metric-item"><strong>Sentences:</strong> ${data.sentence_count}</div>`);
        }
        
        if (data.avg_sentence_length !== undefined) {
            metrics.push(`<div class="metric-item"><strong>Avg Sentence Length:</strong> ${Math.round(data.avg_sentence_length)} words</div>`);
        }
        
        if (data.ai_generated_probability !== undefined) {
            const aiProb = Math.round(data.ai_generated_probability * 100);
            metrics.push(`<div class="metric-item"><strong>AI-Generated Probability:</strong> ${aiProb}%</div>`);
        }
        
        return metrics.join('');
    }

    getContentAnalysisMeaning(data) {
        let meaning = '';
        
        if (data.reading_level) {
            const level = data.reading_level.toLowerCase();
            if (level.includes('college') || level.includes('graduate')) {
                meaning += 'This article is written at an advanced level, which may indicate thorough analysis but could be inaccessible to general readers. ';
            } else if (level.includes('high school')) {
                meaning += 'This article is written at an appropriate level for general audiences, balancing accessibility with substance. ';
            } else {
                meaning += 'This article is written at a basic level, which may oversimplify complex issues. ';
            }
        }
        
        if (data.ai_generated_probability > 0.7) {
            meaning += 'Warning: This content shows signs of being AI-generated, which may lack human editorial oversight. ';
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

    // Enhanced PDF generation
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
    }

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
        addText(`Source: ${article.source || 'Unknown'}`, 12);
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
        const findings = this.generateMeaningfulFindings(this.currentAnalysis);
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
            yPosition += 5;
            
            // Add meaningful analysis for each service
            switch (service.id) {
                case 'source_credibility':
                    this.addSourceCredibilityToPDF(serviceData, addText);
                    break;
                case 'author_analyzer':
                    this.addAuthorAnalysisToPDF(serviceData, addText);
                    break;
                case 'bias_detector':
                    this.addBiasAnalysisToPDF(serviceData, addText);
                    break;
                case 'fact_checker':
                    this.addFactCheckingToPDF(serviceData, addText);
                    break;
                case 'transparency_analyzer':
                    this.addTransparencyAnalysisToPDF(serviceData, addText);
                    break;
                case 'manipulation_detector':
                    this.addManipulationAnalysisToPDF(serviceData, addText);
                    break;
                case 'content_analyzer':
                    this.addContentAnalysisToPDF(serviceData, addText);
                    break;
            }
            
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
    }
    
    addSourceCredibilityToPDF(data, addText) {
        addText('What We Found:', 12, 'bold');
        addText(this.getSourceFindings(data), 11);
        
        addText('What This Means:', 12, 'bold');
        addText(this.getSourceMeaning(data), 11);
        
        if (data.credibility_score !== undefined) {
            addText(`Credibility Score: ${data.credibility_score}/100`, 12, 'bold');
        }
    }
    
    addAuthorAnalysisToPDF(data, addText) {
        addText('Author Profile:', 12, 'bold');
        if (data.author_name) {
            addText(`Name: ${data.author_name}`, 11);
        }
        if (data.verified !== undefined) {
            addText(`Verification Status: ${data.verified ? 'Verified Journalist' : 'Unverified'}`, 11);
        }
        if (data.years_experience !== undefined) {
            addText(`Experience: ${data.years_experience} years`, 11);
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getAuthorMeaning(data), 11);
    }
    
    addBiasAnalysisToPDF(data, addText) {
        addText('Bias Indicators:', 12, 'bold');
        addText(this.getBiasFindings(data), 11);
        
        if (data.loaded_phrases && data.loaded_phrases.length > 0) {
            addText('Examples of Biased Language:', 12, 'bold');
            data.loaded_phrases.slice(0, 3).forEach(phrase => {
                addText(`• "${phrase.phrase}" (${phrase.type || 'Loaded Language'})`, 11);
            });
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getBiasMeaning(data), 11);
    }
    
    addFactCheckingToPDF(data, addText) {
        const total = data.claims_checked || 0;
        const verified = data.verified_count || 0;
        
        addText(`Claims Analyzed: ${total}`, 12, 'bold');
        addText(`Verified as Accurate: ${verified} (${total > 0 ? Math.round((verified/total)*100) : 0}%)`, 11);
        
        if (data.claims && data.claims.length > 0) {
            addText('Sample Claims:', 12, 'bold');
            data.claims.slice(0, 3).forEach(claim => {
                addText(`• "${claim.claim}"`, 11);
                addText(`  Verdict: ${claim.verdict}`, 11);
            });
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getFactCheckerMeaning(data), 11);
    }
    
    addTransparencyAnalysisToPDF(data, addText) {
        addText('Transparency Indicators:', 12, 'bold');
        const items = [
            `Sources Cited: ${data.has_sources ? 'Yes' : 'No'}`,
            `Author Disclosed: ${data.has_author ? 'Yes' : 'No'}`,
            `Funding Disclosed: ${data.has_funding_info ? 'Yes' : 'No'}`,
            `Conflicts Disclosed: ${data.has_disclosure ? 'Yes' : 'No'}`
        ];
        items.forEach(item => addText(`• ${item}`, 11));
        
        addText('What This Means:', 12, 'bold');
        addText(this.getTransparencyMeaning(data), 11);
    }
    
    addManipulationAnalysisToPDF(data, addText) {
        if (data.manipulation_detected) {
            addText('Manipulation Techniques Found:', 12, 'bold');
            if (data.techniques_found && data.techniques_found.length > 0) {
                data.techniques_found.forEach(tech => {
                    addText(`• ${tech.name}: ${tech.description}`, 11);
                });
            }
        } else {
            addText('No manipulation techniques detected.', 11);
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getManipulationMeaning(data), 11);
    }
    
    addContentAnalysisToPDF(data, addText) {
        addText('Content Metrics:', 12, 'bold');
        if (data.reading_level) {
            addText(`Reading Level: ${data.reading_level}`, 11);
        }
        if (data.flesch_score !== undefined) {
            addText(`Readability Score: ${data.flesch_score} (${data.flesch_score > 60 ? 'Easy' : data.flesch_score > 30 ? 'Moderate' : 'Difficult'})`, 11);
        }
        if (data.ai_generated_probability !== undefined) {
            addText(`AI-Generated Probability: ${Math.round(data.ai_generated_probability * 100)}%`, 11);
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getContentAnalysisMeaning(data), 11);
    }
addContentAnalysisToPDF(data, addText) {
        addText('Content Metrics:', 12, 'bold');
        if (data.reading_level) {
            addText(`Reading Level: ${data.reading_level}`, 11);
        }
        if (data.flesch_score !== undefined) {
            addText(`Readability Score: ${data.flesch_score} (${data.flesch_score > 60 ? 'Easy' : data.flesch_score > 30 ? 'Moderate' : 'Difficult'})`, 11);
        }
        if (data.ai_generated_probability !== undefined) {
            addText(`AI-Generated Probability: ${Math.round(data.ai_generated_probability * 100)}%`, 11);
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getContentAnalysisMeaning(data), 11);
    }
    
    // Progress Animation Methods
    showLoading() {
        document.getElementById('loadingOverlay').classList.add('active');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('active');
    }

    showError(message) {
        window.showError(message);
    }

    resetProgress() {
        // Reset any progress indicators if needed
    }

    startProgressAnimation() {
        // Start progress animation if implemented
    }

    stopProgressAnimation() {
        // Stop progress animation if implemented
    }

    completeProgress() {
        // Complete progress animation if implemented
    }

    animateTrustScore(score) {
        const scoreEl = document.getElementById('trustScoreNumber');
        if (!scoreEl) return;

        let current = 0;
        const increment = score / 30;
        const timer = setInterval(() => {
            current += increment;
            if (current >= score) {
                current = score;
                clearInterval(timer);
            }
            scoreEl.textContent = Math.round(current);
        }, 30);
    }

    updateTrustLevelIndicator(score, level) {
        const indicatorEl = document.getElementById('trustLevelIndicator');
        const iconEl = document.getElementById('trustLevelIcon');
        const textEl = document.getElementById('trustLevelText');
        
        if (!indicatorEl || !iconEl || !textEl) return;

        // Remove all level classes
        indicatorEl.className = 'trust-level-indicator';
        
        // Add appropriate class and update text
        if (score >= 80) {
            indicatorEl.classList.add('level-very-high');
            iconEl.className = 'fas fa-check-circle trust-level-icon';
            textEl.textContent = 'Very High Credibility';
        } else if (score >= 60) {
            indicatorEl.classList.add('level-high');
            iconEl.className = 'fas fa-check trust-level-icon';
            textEl.textContent = 'High Credibility';
        } else if (score >= 40) {
            indicatorEl.classList.add('level-moderate');
            iconEl.className = 'fas fa-exclamation-circle trust-level-icon';
            textEl.textContent = 'Moderate Credibility';
        } else if (score >= 20) {
            indicatorEl.classList.add('level-low');
            iconEl.className = 'fas fa-times-circle trust-level-icon';
            textEl.textContent = 'Low Credibility';
        } else {
            indicatorEl.classList.add('level-very-low');
            iconEl.className = 'fas fa-times-circle trust-level-icon';
            textEl.textContent = 'Very Low Credibility';
        }
    }

    displayTrustBreakdown(detailedAnalysis) {
        const container = document.getElementById('trustBreakdown');
        if (!container) return;

        const components = [
            {
                name: 'Source Reputation',
                value: this.extractScore(detailedAnalysis.source_credibility, ['credibility_score', 'score']),
                icon: 'fa-building',
                explanation: this.getSourceCredibilityExplanation(detailedAnalysis.source_credibility)
            },
            {
                name: 'Author Credibility',
                value: this.extractScore(detailedAnalysis.author_analyzer, ['credibility_score', 'score']),
                icon: 'fa-user',
                explanation: this.getAuthorCredibilityExplanation(detailedAnalysis.author_analyzer)
            },
            {
                name: 'Transparency',
                value: this.extractScore(detailedAnalysis.transparency_analyzer, ['transparency_score', 'score']),
                icon: 'fa-eye',
                explanation: this.getTransparencyExplanation(detailedAnalysis.transparency_analyzer)
            },
            {
                name: 'Objectivity',
                value: detailedAnalysis.bias_detector ? 
                    (100 - (detailedAnalysis.bias_detector.overall_bias_score || 0)) : 50,
                icon: 'fa-balance-scale',
                explanation: this.getObjectivityExplanation(detailedAnalysis.bias_detector)
            }
        ];

        container.innerHTML = components.map(comp => {
            const type = this.getBreakdownType(comp.value);
            return `
                <div class="breakdown-item breakdown-${type}">
                    <div class="breakdown-header">
                        <div class="breakdown-label">
                            <div class="breakdown-icon">
                                <i class="fas ${comp.icon}"></i>
                            </div>
                            ${comp.name}
                        </div>
                        <div class="breakdown-value">${comp.value}%</div>
                    </div>
                    <div class="breakdown-explanation">
                        ${comp.explanation}
                    </div>
                    <div class="breakdown-bar">
                        <div class="breakdown-fill" style="width: ${comp.value}%"></div>
                    </div>
                </div>
            `;
        }).join('');
    }

    getBreakdownType(score) {
        if (score >= 70) return 'positive';
        if (score >= 40) return 'neutral';
        if (score >= 20) return 'warning';
        return 'negative';
    }

    displayArticleInfo(article, analysis) {
        const titleEl = document.getElementById('articleTitle');
        const metaEl = document.getElementById('articleMeta');
        
        if (titleEl) {
            titleEl.textContent = article.title || 'Untitled Article';
        }
        
        if (metaEl) {
            const metaItems = [];
            
            if (article.author) {
                metaItems.push(`
                    <div class="meta-item">
                        <i class="fas fa-user"></i>
                        ${article.author}
                    </div>
                `);
            }
            
            if (article.source) {
                metaItems.push(`
                    <div class="meta-item">
                        <i class="fas fa-globe"></i>
                        ${article.source}
                    </div>
                `);
            }
            
            if (article.publish_date) {
                metaItems.push(`
                    <div class="meta-item">
                        <i class="fas fa-calendar"></i>
                        ${new Date(article.publish_date).toLocaleDateString()}
                    </div>
                `);
            }
            
            metaEl.innerHTML = metaItems.join('');
        }
    }

    toggleAccordion(serviceId) {
        const item = document.getElementById(`service-${serviceId}`);
        if (!item) return;

        const wasActive = item.classList.contains('active');
        
        // Close all accordions
        document.querySelectorAll('.service-accordion-item').forEach(el => {
            el.classList.remove('active');
        });
        
        // Open clicked accordion if it wasn't active
        if (!wasActive) {
            item.classList.add('active');
            
            // Initialize any charts in this service
            setTimeout(() => {
                this.initializeServiceCharts(serviceId);
            }, 300);
        }
    }

    initializeServiceCharts(serviceId) {
        // Initialize charts based on service ID
        switch(serviceId) {
            case 'source_credibility':
                // Initialize source credibility charts if needed
                break;
            case 'bias_detector':
                // Initialize bias detection charts if needed
                break;
            // Add other services as needed
        }
    }

    shareResults() {
        if (!this.currentAnalysis) {
            this.showError('No analysis results to share');
            return;
        }

        const shareUrl = window.location.href;
        const shareText = `Check out this news analysis: Trust Score ${this.currentAnalysis.analysis.trust_score}/100`;

        if (navigator.share) {
            navigator.share({
                title: 'TruthLens Analysis',
                text: shareText,
                url: shareUrl
            }).catch(err => console.log('Error sharing:', err));
        } else {
            // Fallback to copying URL
            navigator.clipboard.writeText(shareUrl).then(() => {
                this.showError('Link copied to clipboard!');
            }).catch(err => {
                console.error('Failed to copy:', err);
            });
        }
    }

    loadSampleData() {
        // Load sample data for development/testing
        console.log('Ready to analyze articles');
    }

    // Helper method to extract scores from nested data
    extractScore(data, fields, defaultValue = 50) {
        return window.extractScore(data, fields, defaultValue);
    }

    // Explanation methods that delegate to window functions
    getSourceCredibilityExplanation(data) {
        return window.getSourceCredibilityExplanation(data);
    }

    getAuthorCredibilityExplanation(data) {
        return window.getAuthorCredibilityExplanation(data);
    }

    getTransparencyExplanation(data) {
        const score = this.extractScore(data, ['transparency_score', 'score']);
        if (score >= 80) return "Excellent transparency with proper sourcing and attribution.";
        if (score >= 60) return "Good transparency but missing some attribution details.";
        if (score >= 40) return "Limited transparency makes verification challenging.";
        return "Poor transparency is a significant credibility concern.";
    }

    getObjectivityExplanation(data) {
        return window.getObjectivityExplanation(data);
    }

    getServicePreviewData(serviceId, data) {
        // Implemented in the main method above
        return [];
    }

    getScoreColor(score) {
        return window.getScoreColor(score);
    }

    getScoreClass(score) {
        if (score >= 80) return 'high';
        if (score >= 60) return 'medium';
        if (score >= 40) return 'low';
        return 'very-low';
    }
}

// ============================================================================
// SECTION 3: Initialization
// ============================================================================

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing TruthLens App...');
    window.truthLensApp = new TruthLensApp();
});

// Make app available globally
window.TruthLensApp = TruthLensApp;
