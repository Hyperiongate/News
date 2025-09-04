/**
 * TruthLens News Analyzer - Complete Enhanced Version
 * All 7 issues fixed with AI-powered analysis display
 */

class TruthLensAnalyzer {
    constructor() {
        this.form = document.getElementById('analysisForm');
        this.urlInput = document.getElementById('urlInput');
        this.textInput = document.getElementById('textInput');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.resultsSection = document.getElementById('resultsSection');
        this.progressContainer = document.getElementById('progressContainer');
        this.progressBar = document.getElementById('progressBar');
        this.progressPercentage = document.getElementById('progressPercentage');
        this.progressSteps = document.getElementById('progressSteps');
        this.serviceContainer = document.getElementById('serviceAnalysisContainer');
        
        // Service definitions - REMOVED plagiarismDetector
        this.services = [
            { id: 'sourceCredibility', name: 'Source Credibility Analysis', icon: 'fa-shield-alt' },
            { id: 'biasDetector', name: 'Bias Detection Analysis', icon: 'fa-balance-scale' },
            { id: 'factChecker', name: 'Fact Checking Analysis', icon: 'fa-check-double' },
            { id: 'transparencyAnalyzer', name: 'Transparency Analysis', icon: 'fa-eye' },
            { id: 'manipulationDetector', name: 'Manipulation Detection', icon: 'fa-exclamation-triangle' },
            { id: 'contentAnalyzer', name: 'Content Analysis', icon: 'fa-file-alt' },
            { id: 'author', name: 'Author Analysis', icon: 'fa-user-shield' }
        ];
        
        this.init();
        this.createServiceCards();
    }

    init() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.resetBtn.addEventListener('click', this.handleReset.bind(this));
        
        // Clear other input when one is filled
        this.urlInput.addEventListener('input', () => {
            if (this.urlInput.value) {
                this.textInput.value = '';
            }
        });
        
        this.textInput.addEventListener('input', () => {
            if (this.textInput.value) {
                this.urlInput.value = '';
            }
        });
    }

    createServiceCards() {
        // Generate service analysis cards dynamically
        this.services.forEach(service => {
            const dropdown = this.createServiceDropdown(service);
            this.serviceContainer.appendChild(dropdown);
        });
    }

    createServiceDropdown(service) {
        const dropdown = document.createElement('div');
        dropdown.className = `service-dropdown ${service.id}-dropdown`;
        dropdown.id = `${service.id}Dropdown`;
        
        dropdown.innerHTML = `
            <div class="service-dropdown-header" onclick="toggleServiceDropdown('${service.id}')">
                <h3>
                    <i class="fas ${service.icon}"></i>
                    ${service.name}
                </h3>
                <i class="fas fa-chevron-down dropdown-arrow"></i>
            </div>
            <div class="service-card" id="${service.id}Card">
                ${this.getServiceCardContent(service.id)}
            </div>
        `;
        
        return dropdown;
    }

    getServiceCardContent(serviceId) {
        // Service-specific card content
        const templates = {
            sourceCredibility: this.getSourceCredibilityTemplate(),
            biasDetector: this.getBiasDetectorTemplate(),
            factChecker: this.getFactCheckerTemplate(),
            transparencyAnalyzer: this.getTransparencyAnalyzerTemplate(),
            manipulationDetector: this.getManipulationDetectorTemplate(),
            contentAnalyzer: this.getContentAnalyzerTemplate(),
            author: this.getAuthorAnalysisTemplate()
        };
        
        return templates[serviceId] || '<div>Service template not found</div>';
    }

    getSourceCredibilityTemplate() {
        return `
            <div class="service-card-grid">
                <div class="service-metric">
                    <div class="metric-label">Credibility Score</div>
                    <div class="metric-value" id="sourceCredibilityScore">0/100</div>
                    <div class="metric-description">Overall source reliability assessment</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Source Rating</div>
                    <div class="metric-value" id="sourceCredibilityRating">Unknown</div>
                    <div class="metric-description">Industry credibility classification</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Bias Level</div>
                    <div class="metric-value" id="sourceBiasLevel">Unknown</div>
                    <div class="metric-description">Political/ideological bias assessment</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Domain Age</div>
                    <div class="metric-value" id="sourceDomainAge">Unknown</div>
                    <div class="metric-description">Website establishment timeline</div>
                </div>
            </div>
            
            <div class="service-findings">
                <div class="findings-title">
                    <i class="fas fa-search"></i>
                    Analysis Details
                </div>
                <div class="findings-list" id="sourceCredibilityFindings">
                    <!-- Dynamic findings will be inserted here -->
                </div>
            </div>
            
            <div class="service-interpretation">
                <div class="interpretation-title">Analysis Summary</div>
                <div class="interpretation-text" id="sourceCredibilityInterpretation">
                    Loading source credibility analysis...
                </div>
            </div>
        `;
    }

    getBiasDetectorTemplate() {
        return `
            <div class="service-card-grid">
                <div class="service-metric">
                    <div class="metric-label">Bias Score</div>
                    <div class="metric-value" id="biasScore">0/100</div>
                    <div class="metric-description">Overall bias intensity measurement</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Political Lean</div>
                    <div class="metric-value" id="politicalLean">Neutral</div>
                    <div class="metric-description">Political orientation assessment</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Dominant Bias</div>
                    <div class="metric-value" id="dominantBias">None</div>
                    <div class="metric-description">Primary bias category detected</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Objectivity Score</div>
                    <div class="metric-value" id="objectivityScore">100%</div>
                    <div class="metric-description">Content neutrality assessment</div>
                </div>
            </div>
            
            <!-- Visual Bias Meter -->
            <div class="bias-meter-container">
                <h4 class="meter-title">Political Bias Spectrum</h4>
                <div class="bias-meter">
                    <div class="bias-scale">
                        <span class="scale-label left">Far Left</span>
                        <span class="scale-label">Left</span>
                        <span class="scale-label">Center</span>
                        <span class="scale-label">Right</span>
                        <span class="scale-label right">Far Right</span>
                    </div>
                    <div class="bias-track">
                        <div class="bias-indicator" id="biasIndicator"></div>
                    </div>
                </div>
            </div>
            
            <div class="service-findings">
                <div class="findings-title">
                    <i class="fas fa-search"></i>
                    Analysis Details
                </div>
                <div class="findings-list" id="biasDetectorFindings">
                    <!-- Dynamic findings will be inserted here -->
                </div>
            </div>
            
            <div class="service-interpretation">
                <div class="interpretation-title">Analysis Summary</div>
                <div class="interpretation-text" id="biasDetectorInterpretation">
                    Loading bias detection analysis...
                </div>
            </div>
        `;
    }

    getFactCheckerTemplate() {
        return `
            <div class="service-card-grid">
                <div class="service-metric">
                    <div class="metric-label">Verification Score</div>
                    <div class="metric-value" id="verificationScore">0/100</div>
                    <div class="metric-description">Overall claim verification accuracy</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Claims Analyzed</div>
                    <div class="metric-value" id="claimsAnalyzed">0</div>
                    <div class="metric-description">Total verifiable claims found</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Claims Verified</div>
                    <div class="metric-value" id="claimsVerified">0</div>
                    <div class="metric-description">Claims confirmed as accurate</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Verification Level</div>
                    <div class="metric-value" id="verificationLevel">Unknown</div>
                    <div class="metric-description">Overall fact-checking assessment</div>
                </div>
            </div>
            
            <!-- Actual Claims List -->
            <div class="claims-checked-section" id="claimsCheckedSection" style="display: none;">
                <h4 class="section-title">
                    <i class="fas fa-list-check"></i>
                    Claims Verified
                </h4>
                <div class="claims-list" id="verifiedClaimsList">
                    <!-- Actual claims will be listed here -->
                </div>
            </div>
            
            <div class="service-findings">
                <div class="findings-title">
                    <i class="fas fa-search"></i>
                    Analysis Details
                </div>
                <div class="findings-list" id="factCheckerFindings">
                    <!-- Dynamic findings will be inserted here -->
                </div>
            </div>
            
            <div class="service-interpretation">
                <div class="interpretation-title">Analysis Summary</div>
                <div class="interpretation-text" id="factCheckerInterpretation">
                    Loading fact checking analysis...
                </div>
            </div>
        `;
    }

    getTransparencyAnalyzerTemplate() {
        return `
            <div class="service-card-grid">
                <div class="service-metric">
                    <div class="metric-label">Transparency Score</div>
                    <div class="metric-value" id="transparencyScore">0/100</div>
                    <div class="metric-description">Overall transparency assessment</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Sources Cited</div>
                    <div class="metric-value" id="sourcesCited">0</div>
                    <div class="metric-description">Number of sources referenced</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Quotes Used</div>
                    <div class="metric-value" id="quotesUsed">0</div>
                    <div class="metric-description">Direct quotations included</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Disclosure Level</div>
                    <div class="metric-value" id="disclosureLevel">Unknown</div>
                    <div class="metric-description">Transparency and disclosure quality</div>
                </div>
            </div>
            
            <div class="service-findings">
                <div class="findings-title">
                    <i class="fas fa-search"></i>
                    Analysis Details
                </div>
                <div class="findings-list" id="transparencyAnalyzerFindings">
                    <!-- Dynamic findings will be inserted here -->
                </div>
            </div>
            
            <div class="service-interpretation">
                <div class="interpretation-title">Analysis Summary</div>
                <div class="interpretation-text" id="transparencyAnalyzerInterpretation">
                    Loading transparency analysis...
                </div>
            </div>
        `;
    }

    getManipulationDetectorTemplate() {
        return `
            <div class="service-card-grid">
                <div class="service-metric">
                    <div class="metric-label">Manipulation Score</div>
                    <div class="metric-value" id="manipulationScore">0/100</div>
                    <div class="metric-description">Overall manipulation risk assessment</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Risk Level</div>
                    <div class="metric-value" id="manipulationRiskLevel">Low</div>
                    <div class="metric-description">Manipulation risk classification</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Techniques Found</div>
                    <div class="metric-value" id="manipulationTechniques">0</div>
                    <div class="metric-description">Number of manipulation techniques detected</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Emotional Language</div>
                    <div class="metric-value" id="emotionalLanguageCount">0</div>
                    <div class="metric-description">Emotionally charged words detected</div>
                </div>
            </div>
            
            <div class="service-findings">
                <div class="findings-title">
                    <i class="fas fa-search"></i>
                    Analysis Details
                </div>
                <div class="findings-list" id="manipulationDetectorFindings">
                    <!-- Dynamic findings will be inserted here -->
                </div>
            </div>
            
            <div class="service-interpretation">
                <div class="interpretation-title">Analysis Summary</div>
                <div class="interpretation-text" id="manipulationDetectorInterpretation">
                    Loading manipulation detection analysis...
                </div>
            </div>
        `;
    }

    getContentAnalyzerTemplate() {
        return `
            <div class="service-card-grid">
                <div class="service-metric">
                    <div class="metric-label">Quality Score</div>
                    <div class="metric-value" id="contentQualityScore">0/100</div>
                    <div class="metric-description">Overall content quality assessment</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Content Quality</div>
                    <div class="metric-value" id="contentQualityLevel">Unknown</div>
                    <div class="metric-description">Quality classification level</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Readability</div>
                    <div class="metric-value" id="contentReadability">Unknown</div>
                    <div class="metric-description">Content readability assessment</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Structure Score</div>
                    <div class="metric-value" id="contentStructureScore">Unknown</div>
                    <div class="metric-description">Content organization and structure</div>
                </div>
            </div>
            
            <!-- AI Enhancement Display -->
            <div class="ai-enhancement-section" id="aiEnhancementSection" style="display: none;">
                <h4 class="section-title">
                    <i class="fas fa-robot"></i>
                    AI-Enhanced Analysis
                </h4>
                <div class="ai-summary" id="aiSummaryContent">
                    <!-- AI-generated insights will appear here -->
                </div>
            </div>
            
            <div class="service-findings">
                <div class="findings-title">
                    <i class="fas fa-search"></i>
                    Analysis Details
                </div>
                <div class="findings-list" id="contentAnalyzerFindings">
                    <!-- Dynamic findings will be inserted here -->
                </div>
            </div>
            
            <div class="service-interpretation">
                <div class="interpretation-title">Analysis Summary</div>
                <div class="interpretation-text" id="contentAnalyzerInterpretation">
                    Loading content analysis...
                </div>
            </div>
        `;
    }

    getAuthorAnalysisTemplate() {
        return `
            <!-- Header with Photo and Basic Info -->
            <div class="author-card-header">
                <div class="author-photo-container">
                    <img id="authorPhoto" class="author-photo" src="" alt="Author photo" style="display: none;">
                    <div id="authorPhotoPlaceholder" class="author-photo-placeholder">
                        <i class="fas fa-user"></i>
                    </div>
                    <div id="verificationBadge" class="verification-badge" style="display: none;">
                        <i class="fas fa-check"></i>
                    </div>
                </div>
                <div class="author-header-info">
                    <h3 class="author-name" id="authorName">Author Name</h3>
                    <p class="author-position" id="authorPosition">Professional Journalist</p>
                    <div class="author-credibility">
                        <span class="credibility-label">Credibility:</span>
                        <span class="credibility-score" id="authorCredibilityScore">0/100</span>
                    </div>
                </div>
            </div>

            <!-- Professional Profile Links -->
            <div class="author-profiles" id="authorProfiles" style="display: none;">
                <h4 class="author-section-title">
                    <i class="fas fa-link"></i>
                    Professional Profiles
                </h4>
                <div class="profiles-grid" id="profilesGrid">
                    <!-- Profile links will be inserted here -->
                </div>
            </div>

            <!-- Quick Stats -->
            <div class="author-stats" id="authorStats">
                <div class="stat-item">
                    <span class="stat-number" id="articleCount">0</span>
                    <span class="stat-label">Articles</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number" id="profilesCount">0</span>
                    <span class="stat-label">Profiles</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number" id="awardsCount">0</span>
                    <span class="stat-label">Awards</span>
                </div>
            </div>

            <!-- Biography -->
            <div class="author-bio" id="authorBio" style="display: none;">
                <h4 class="author-section-title">
                    <i class="fas fa-user-circle"></i>
                    Biography
                </h4>
                <p class="author-bio-text" id="authorBioText"></p>
            </div>

            <!-- Areas of Expertise -->
            <div class="expertise-section" id="expertiseSection" style="display: none;">
                <h4 class="author-section-title">
                    <i class="fas fa-brain"></i>
                    Areas of Expertise
                </h4>
                <div class="expertise-tags" id="expertiseTags">
                    <!-- Expertise tags will be inserted here -->
                </div>
            </div>

            <!-- Publication History -->
            <div class="publication-section" id="publicationSection" style="display: none;">
                <h4 class="author-section-title">
                    <i class="fas fa-newspaper"></i>
                    Recent Publications
                </h4>
                <div class="publication-list" id="publicationList">
                    <!-- Publications will be listed here -->
                </div>
            </div>

            <!-- Awards (if any) -->
            <div class="awards-section" id="awardsSection" style="display: none;">
                <h4 class="author-section-title">
                    <i class="fas fa-trophy"></i>
                    Awards & Recognition
                </h4>
                <div class="awards-list" id="awardsList">
                    <!-- Awards will be inserted here -->
                </div>
            </div>
        `;
    }

    handleReset() {
        this.urlInput.value = '';
        this.textInput.value = '';
        this.resultsSection.classList.remove('show');
        this.progressContainer.classList.remove('active');
        this.resetProgress();
        
        // Reset all service dropdowns
        const dropdowns = document.querySelectorAll('.service-dropdown');
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove('expanded');
        });
        
        // Hide plagiarism detector if it exists
        const plagiarismDropdown = document.getElementById('plagiarismDetectorDropdown');
        if (plagiarismDropdown) {
            plagiarismDropdown.style.display = 'none';
        }
        
        document.getElementById('debugInfo').style.display = 'none';
        this.hideError();
        this.urlInput.focus();
        this.form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const url = this.urlInput.value.trim();
        const text = this.textInput.value.trim();
        
        if (!url && !text) {
            this.showError('Please provide either a URL or article text');
            return;
        }

        // Validate URL format if URL is provided
        if (url) {
            try {
                new URL(url);
            } catch (e) {
                this.showError('Please enter a valid URL starting with http:// or https://');
                return;
            }
        }

        // Validate text length if text is provided
        if (text) {
            const wordCount = text.trim().split(/\s+/).filter(word => word.length > 0).length;
            if (wordCount < 50) {
                this.showError(`Please enter at least 50 words for analysis (current: ${wordCount} words)`);
                return;
            }
        }

        this.setLoading(true);
        this.startProgress();
        
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url || undefined,
                    text: text || undefined
                })
            });

            const data = await response.json();
            console.log('Response received:', data);
            
            if (response.ok && data.success !== false) {
                this.displayResults(data);
            } else {
                this.showError(data.error || data.message || 'Analysis failed');
            }
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            this.setLoading(false);
        }
    }

    startProgress() {
        this.progressContainer.classList.add('active');
        this.resetProgress();
        
        setTimeout(() => {
            this.progressContainer.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center'
            });
        }, 100);
        
        let currentStep = 0;
        let progress = 0;
        
        const steps = [
            { progress: 15, duration: 2000 },
            { progress: 30, duration: 3000 },
            { progress: 50, duration: 4000 },
            { progress: 70, duration: 3500 },
            { progress: 85, duration: 2500 },
            { progress: 100, duration: 2000 }
        ];

        const updateProgress = () => {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                const startProgress = progress;
                const endProgress = step.progress;
                const duration = step.duration;
                const startTime = Date.now();
                
                this.setActiveStep(currentStep);
                
                const animate = () => {
                    const elapsed = Date.now() - startTime;
                    const progressRatio = Math.min(elapsed / duration, 1);
                    const easeOut = 1 - Math.pow(1 - progressRatio, 3);
                    progress = startProgress + (endProgress - startProgress) * easeOut;
                    
                    this.updateProgressBar(progress);
                    
                    if (progressRatio < 1) {
                        requestAnimationFrame(animate);
                    } else {
                        this.setStepCompleted(currentStep);
                        currentStep++;
                        
                        if (currentStep < steps.length) {
                            setTimeout(updateProgress, 200);
                        }
                    }
                };
                
                animate();
            }
        };
        
        updateProgress();
    }

    resetProgress() {
        this.updateProgressBar(0);
        const steps = this.progressSteps.querySelectorAll('.progress-step');
        steps.forEach(step => {
            step.classList.remove('active', 'completed');
        });
    }

    updateProgressBar(progress) {
        this.progressBar.style.width = progress + '%';
        this.progressPercentage.textContent = Math.round(progress) + '%';
    }

    setActiveStep(stepIndex) {
        const steps = this.progressSteps.querySelectorAll('.progress-step');
        steps.forEach((step, index) => {
            if (index === stepIndex) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
    }

    setStepCompleted(stepIndex) {
        const step = this.progressSteps.querySelector(`[data-step="${stepIndex}"]`);
        if (step) {
            step.classList.remove('active');
            step.classList.add('completed');
            step.querySelector('.step-icon').innerHTML = '<i class="fas fa-check"></i>';
        }
    }

    displayResults(data) {
        this.progressContainer.classList.remove('active');
        this.showDebugInfo(data);
        
        let trustScore = data.trust_score || 0;
        let articleSummary = data.article_summary || 'Analysis completed';
        let source = data.source || 'Unknown Source';
        let author = data.author || 'Staff Writer';
        let findingsSummary = data.findings_summary || 'Analysis completed successfully';
        
        this.updateTrustScore(trustScore);
        
        const overviewEl = document.getElementById('analysisOverview');
        overviewEl.classList.remove('trust-high', 'trust-medium', 'trust-low');
        if (trustScore >= 70) {
            overviewEl.classList.add('trust-high');
        } else if (trustScore >= 40) {
            overviewEl.classList.add('trust-medium');
        } else {
            overviewEl.classList.add('trust-low');
        }
        
        document.getElementById('articleSummary').textContent = 
            articleSummary.length > 100 ? articleSummary.substring(0, 100) + '...' : articleSummary;
        document.getElementById('articleSource').textContent = source;
        document.getElementById('articleAuthor').textContent = author;
        document.getElementById('findingsSummary').textContent = findingsSummary;
        
        // Display all service analyses with rich functionality
        this.displayAllServiceAnalyses(data);
        this.showResults();
    }

    updateTrustScore(score) {
        const scoreElement = document.getElementById('trustScore');
        const labelElement = document.getElementById('trustLabel');
        
        scoreElement.textContent = Math.round(score);
        
        if (score >= 80) {
            labelElement.textContent = 'Highly Trustworthy';
            scoreElement.className = 'trust-score-number trust-high';
        } else if (score >= 60) {
            labelElement.textContent = 'Generally Trustworthy';
            scoreElement.className = 'trust-score-number trust-medium';
        } else if (score >= 40) {
            labelElement.textContent = 'Moderate Trust';
            scoreElement.className = 'trust-score-number trust-medium';
        } else {
            labelElement.textContent = 'Low Trustworthiness';
            scoreElement.className = 'trust-score-number trust-low';
        }
    }

    displayAllServiceAnalyses(data) {
        console.log('=== Displaying All Service Analyses ===');
        console.log('Data received:', data);
        
        const detailed_analysis = data.detailed_analysis || {};
        
        // Hide plagiarism detector completely
        const plagiarismDropdown = document.getElementById('plagiarismDetectorDropdown');
        if (plagiarismDropdown) {
            plagiarismDropdown.style.display = 'none';
        }
        
        // Display each service analysis with enhanced AI-powered content
        this.displaySourceCredibility(detailed_analysis.source_credibility || {});
        this.displayBiasDetection(detailed_analysis.bias_detector || {});
        this.displayFactChecking(detailed_analysis.fact_checker || {});
        this.displayTransparencyAnalysis(detailed_analysis.transparency_analyzer || {});
        this.displayManipulationDetection(detailed_analysis.manipulation_detector || {});
        this.displayContentAnalysis(detailed_analysis.content_analyzer || {}, detailed_analysis.openai_enhancer || {});
        this.displayAuthorAnalysis(detailed_analysis.author_analyzer || {}, data.author);
    }

    // ENHANCED SERVICE DISPLAY METHODS WITH AI-POWERED ANALYSIS

    displaySourceCredibility(data) {
        const score = data.score || data.credibility_score || 0;
        const rating = data.credibility || data.credibility_level || 'Unknown';
        const biasLevel = data.bias || data.bias_level || 'Unknown';
        const domainAge = data.domain_age_days ? this.formatDomainAge(data.domain_age_days) : 'Unknown';
        
        // Generate AI analysis
        const whatWeLooked = data.analysis?.what_we_looked || 
            "We evaluated the news source's historical accuracy, editorial standards, ownership transparency, correction policies, and journalistic practices. We examined their track record, fact-checking history, and industry recognition.";
        
        const whatWeFound = data.analysis?.what_we_found || this.generateCredibilityFindings(score, rating, biasLevel, data);
        
        const whatItMeans = data.analysis?.what_it_means || this.generateCredibilityMeaning(score, rating);
        
        document.getElementById('sourceCredibilityScore').textContent = `${score}/100`;
        document.getElementById('sourceCredibilityRating').textContent = rating;
        document.getElementById('sourceBiasLevel').textContent = biasLevel;
        document.getElementById('sourceDomainAge').textContent = domainAge;
        
        const findingsContainer = document.getElementById('sourceCredibilityFindings');
        if (findingsContainer) {
            findingsContainer.innerHTML = `
                <div class="service-analysis-section">
                    <div class="analysis-block">
                        <h4><i class="fas fa-search"></i> What We Analyzed</h4>
                        <p>${whatWeLooked}</p>
                    </div>
                    <div class="analysis-block">
                        <h4><i class="fas fa-clipboard-check"></i> What We Found</h4>
                        <p>${whatWeFound}</p>
                    </div>
                    <div class="analysis-block">
                        <h4><i class="fas fa-lightbulb"></i> What This Means</h4>
                        <p>${whatItMeans}</p>
                    </div>
                </div>
            `;
        }
        
        document.getElementById('sourceCredibilityInterpretation').textContent = 
            data.interpretation || `${whatWeFound} ${whatItMeans}`;
    }

    displayBiasDetection(data) {
        const biasScore = data.bias_score || data.score || 0;
        const politicalLean = data.dimensions?.political?.label || data.political_lean || 'Neutral';
        const dominantBias = data.dominant_bias || 'None';
        const objectivityScore = data.objectivity_score !== undefined ? data.objectivity_score : (100 - biasScore);
        
        const whatWeLooked = data.analysis?.what_we_looked || 
            "We analyzed language patterns, source selection, framing techniques, and narrative balance. Our AI examined word choice, emotional tone, political indicators, and representation of different viewpoints.";
        
        const whatWeFound = data.analysis?.what_we_found || this.generateBiasFindings(biasScore, politicalLean, dominantBias);
        
        const whatItMeans = data.analysis?.what_it_means || this.generateBiasMeaning(biasScore, objectivityScore);
        
        document.getElementById('biasScore').textContent = `${biasScore}/100`;
        document.getElementById('politicalLean').textContent = politicalLean;
        document.getElementById('dominantBias').textContent = dominantBias;
        document.getElementById('objectivityScore').textContent = `${objectivityScore}%`;
        
        // Update bias meter
        this.updateBiasMeter(politicalLean, biasScore);
        
        const findingsContainer = document.getElementById('biasDetectorFindings');
        if (findingsContainer) {
            findingsContainer.innerHTML = `
                <div class="service-analysis-section">
                    <div class="analysis-block">
                        <h4><i class="fas fa-search"></i> What We Analyzed</h4>
                        <p>${whatWeLooked}</p>
                    </div>
                    <div class="analysis-block">
                        <h4><i class="fas fa-clipboard-check"></i> What We Found</h4>
                        <p>${whatWeFound}</p>
                    </div>
                    <div class="analysis-block">
                        <h4><i class="fas fa-lightbulb"></i> What This Means</h4>
                        <p>${whatItMeans}</p>
                    </div>
                </div>
            `;
        }
        
        document.getElementById('biasDetectorInterpretation').textContent = 
            data.interpretation || `${whatWeFound} ${whatItMeans}`;
    }

    displayFactChecking(data) {
        const claimsAnalyzed = data.claims_found || data.claims_analyzed || 0;
        const claimsVerified = data.claims_verified || 0;
        
        // FIXED: Calculate correct verification score
        let verificationScore = 0;
        if (claimsAnalyzed > 0) {
            verificationScore = Math.round((claimsVerified / claimsAnalyzed) * 100);
        } else {
            verificationScore = data.score || 0;
        }
        
        const verificationLevel = this.getVerificationLevel(verificationScore);
        
        const whatWeLooked = data.analysis?.what_we_looked || 
            "We identified and examined verifiable claims in the article, checking them against authoritative sources, official records, and fact-checking databases. Each claim was evaluated for accuracy and context.";
        
        const whatWeFound = data.analysis?.what_we_found || this.generateFactCheckFindings(claimsAnalyzed, claimsVerified, data.claims);
        
        const whatItMeans = data.analysis?.what_it_means || this.generateFactCheckMeaning(verificationScore, verificationLevel);
        
        document.getElementById('verificationScore').textContent = `${verificationScore}/100`;
        document.getElementById('claimsAnalyzed').textContent = claimsAnalyzed;
        document.getElementById('claimsVerified').textContent = claimsVerified;
        document.getElementById('verificationLevel').textContent = verificationLevel;
        
        // Display actual claims if available
        this.displayClaimsList(data);
        
        const findingsContainer = document.getElementById('factCheckerFindings');
        if (findingsContainer) {
            findingsContainer.innerHTML = `
                <div class="service-analysis-section">
                    <div class="analysis-block">
                        <h4><i class="fas fa-search"></i> What We Analyzed</h4>
                        <p>${whatWeLooked}</p>
                    </div>
                    <div class="analysis-block">
                        <h4><i class="fas fa-clipboard-check"></i> What We Found</h4>
                        <p>${whatWeFound}</p>
                    </div>
                    <div class="analysis-block">
                        <h4><i class="fas fa-lightbulb"></i> What This Means</h4>
                        <p>${whatItMeans}</p>
                    </div>
                </div>
            `;
        }
        
        document.getElementById('factCheckerInterpretation').textContent = 
            data.interpretation || `${whatWeFound} ${whatItMeans}`;
    }

    displayTransparencyAnalysis(data) {
        const sourcesCited = data.source_count || data.sources_cited || 0;
        const quotesUsed = data.quote_count || data.quotes_used || 0;
        
        // FIXED: Always calculate transparency score based on sources and quotes
        // Ignore backend score if we have source/quote data
        let transparencyScore;
        if (sourcesCited > 0 || quotesUsed > 0) {
            // Calculate based on actual sources and quotes
            const sourceScore = Math.min(sourcesCited * 8, 50);  // Max 50 points
            const quoteScore = Math.min(quotesUsed * 10, 50);   // Max 50 points
            transparencyScore = Math.min(sourceScore + quoteScore, 100);
        } else {
            // Only use backend score if no source/quote data
            transparencyScore = data.score || data.transparency_score || 0;
        }
        
        const disclosureLevel = this.getTransparencyLevel(transparencyScore, sourcesCited, quotesUsed);
        
        const whatWeLooked = data.analysis?.what_we_looked || 
            "We examined source attribution, quote usage, data transparency, conflict of interest disclosures, and methodology explanations. We evaluated how clearly the article presents its information sources and evidence.";
        
        const whatWeFound = data.analysis?.what_we_found || this.generateTransparencyFindings(sourcesCited, quotesUsed, transparencyScore);
        
        const whatItMeans = data.analysis?.what_it_means || this.generateTransparencyMeaning(disclosureLevel, transparencyScore);
        
        document.getElementById('transparencyScore').textContent = `${transparencyScore}/100`;
        document.getElementById('sourcesCited').textContent = sourcesCited;
        document.getElementById('quotesUsed').textContent = quotesUsed;
        document.getElementById('disclosureLevel').textContent = disclosureLevel;
        
        const findingsContainer = document.getElementById('transparencyAnalyzerFindings');
        if (findingsContainer) {
            findingsContainer.innerHTML = `
                <div class="service-analysis-section">
                    <div class="analysis-block">
                        <h4><i class="fas fa-search"></i> What We Analyzed</h4>
                        <p>${whatWeLooked}</p>
                    </div>
                    <div class="analysis-block">
                        <h4><i class="fas fa-clipboard-check"></i> What We Found</h4>
                        <p>${whatWeFound}</p>
                    </div>
                    <div class="analysis-block">
                        <h4><i class="fas fa-lightbulb"></i> What This Means</h4>
                        <p>${whatItMeans}</p>
                    </div>
                </div>
            `;
        }
        
        document.getElementById('transparencyAnalyzerInterpretation').textContent = 
            data.interpretation || `${whatWeFound} ${whatItMeans}`;
    }

    displayManipulationDetection(data) {
        const manipulationScore = data.score || data.manipulation_score || 0;
        const riskLevel = this.getManipulationRiskLevel(manipulationScore);
        const techniques = data.manipulation_techniques || [];
        const emotionalCount = data.emotional_language_count || data.emotional_words || 0;
        
        const whatWeLooked = data.analysis?.what_we_looked || 
            "We examined the article for manipulation techniques including emotional language patterns, logical fallacies, misleading framing, selective fact presentation, and propaganda techniques. Our analysis evaluated word choice, narrative structure, and rhetorical devices.";
        
        const whatWeFound = data.analysis?.what_we_found || this.generateManipulationFindings(manipulationScore, techniques, emotionalCount);
        
        const whatItMeans = data.analysis?.what_it_means || this.generateManipulationMeaning(manipulationScore, riskLevel);
        
        document.getElementById('manipulationScore').textContent = `${manipulationScore}/100`;
        document.getElementById('manipulationRiskLevel').textContent = riskLevel;
        document.getElementById('manipulationTechniques').textContent = techniques.length;
        document.getElementById('emotionalLanguageCount').textContent = emotionalCount;
        
        const findingsContainer = document.getElementById('manipulationDetectorFindings');
        if (findingsContainer) {
            findingsContainer.innerHTML = `
                <div class="service-analysis-section">
                    <div class="analysis-block">
                        <h4><i class="fas fa-search"></i> What We Analyzed</h4>
                        <p>${whatWeLooked}</p>
                    </div>
                    <div class="analysis-block">
                        <h4><i class="fas fa-clipboard-check"></i> What We Found</h4>
                        <p>${whatWeFound}</p>
                    </div>
                    <div class="analysis-block">
                        <h4><i class="fas fa-lightbulb"></i> What This Means</h4>
                        <p>${whatItMeans}</p>
                    </div>
                </div>
            `;
        }
        
        document.getElementById('manipulationDetectorInterpretation').textContent = 
            data.interpretation || `${whatWeFound} ${whatItMeans}`;
    }

    displayContentAnalysis(contentData, openaiData) {
        const qualityScore = contentData.score || contentData.quality_score || 0;
        const qualityLevel = this.getQualityLevel(qualityScore);
        const readability = contentData.readability || contentData.readability_score || 'Unknown';
        const structureScore = contentData.structure_score || contentData.organization_score || 'Unknown';
        
        // Integrate OpenAI insights
        const aiInsights = openaiData?.summary || openaiData?.enhanced_summary || '';
        const keyPoints = openaiData?.key_points || [];
        
        const whatWeLooked = contentData.analysis?.what_we_looked || 
            "We evaluated writing quality, logical structure, evidence presentation, and journalistic standards. Our AI analyzed readability, coherence, factual density, and adherence to professional reporting practices.";
        
        const whatWeFound = contentData.analysis?.what_we_found || this.generateContentFindings(qualityScore, readability, aiInsights, keyPoints);
        
        const whatItMeans = contentData.analysis?.what_it_means || this.generateContentMeaning(qualityLevel, qualityScore);
        
        document.getElementById('contentQualityScore').textContent = `${qualityScore}/100`;
        document.getElementById('contentQualityLevel').textContent = qualityLevel;
        document.getElementById('contentReadability').textContent = readability;
        document.getElementById('contentStructureScore').textContent = structureScore;
        
        // Display OpenAI enhancement if available
        if (aiInsights || keyPoints.length > 0) {
            const aiSection = document.getElementById('aiEnhancementSection');
            const aiContent = document.getElementById('aiSummaryContent');
            if (aiSection && aiContent) {
                aiSection.style.display = 'block';
                aiContent.innerHTML = `
                    <div class="ai-insight">
                        <h5>AI-Generated Analysis</h5>
                        <p>${aiInsights}</p>
                        ${keyPoints.length > 0 ? `
                            <h5>Key Insights</h5>
                            <ul>
                                ${keyPoints.map(point => `<li>${point}</li>`).join('')}
                            </ul>
                        ` : ''}
                    </div>
                `;
            }
        }
        
        const findingsContainer = document.getElementById('contentAnalyzerFindings');
        if (findingsContainer) {
            findingsContainer.innerHTML = `
                <div class="service-analysis-section">
                    <div class="analysis-block">
                        <h4><i class="fas fa-search"></i> What We Analyzed</h4>
                        <p>${whatWeLooked}</p>
                    </div>
                    <div class="analysis-block">
                        <h4><i class="fas fa-clipboard-check"></i> What We Found</h4>
                        <p>${whatWeFound}</p>
                    </div>
                    <div class="analysis-block">
                        <h4><i class="fas fa-lightbulb"></i> What This Means</h4>
                        <p>${whatItMeans}</p>
                    </div>
                </div>
            `;
        }
        
        document.getElementById('contentAnalyzerInterpretation').textContent = 
            contentData.interpretation || `${whatWeFound} ${whatItMeans}`;
    }

    displayAuthorAnalysis(data, fallbackAuthor) {
        console.log('=== Displaying Author Analysis ===');
        console.log('Author data:', data);
        
        // Extract comprehensive author information
        const authorName = data.author_name || data.name || fallbackAuthor || 'Unknown';
        const authorScore = data.score || data.credibility_score || data.author_score || 0;
        const authorPosition = data.position || data.title || 'Writer';
        const authorOrganization = data.organization || '';
        const authorBio = data.bio || data.biography || '';
        const hasVerification = data.verified || false;
        
        // Combine position and organization
        const fullPosition = authorOrganization && !authorPosition.includes(authorOrganization) 
            ? `${authorPosition} at ${authorOrganization}` 
            : authorPosition;
        
        // Update basic information
        document.getElementById('authorName').textContent = authorName;
        document.getElementById('authorPosition').textContent = fullPosition;
        document.getElementById('authorCredibilityScore').textContent = authorScore > 0 ? `${authorScore}/100` : 'N/A';
        
        // Update credibility score styling
        this.updateAuthorCredibilityStyle(authorScore);
        
        // Extract and display profiles
        const profiles = this.extractAuthorProfiles(data);
        this.displayAuthorProfiles(profiles);
        
        // Extract and display publication history
        const publications = data.recent_articles || data.publication_history || [];
        this.displayPublicationHistory(publications);
        
        // Update stats
        const profilesCount = Object.values(profiles).filter(url => url).length;
        const articleCount = data.article_count || publications.length || 0;
        const awardsCount = data.awards?.length || data.awards_recognition?.length || 0;
        
        document.getElementById('articleCount').textContent = articleCount;
        document.getElementById('profilesCount').textContent = profilesCount;
        document.getElementById('awardsCount').textContent = awardsCount;
        
        // Display biography
        if (authorBio && authorBio.trim()) {
            document.getElementById('authorBio').style.display = 'block';
            document.getElementById('authorBioText').textContent = authorBio;
        } else {
            document.getElementById('authorBio').style.display = 'none';
        }
        
        // Display verification badge
        document.getElementById('verificationBadge').style.display = hasVerification ? 'flex' : 'none';
        
        // Display expertise areas
        const expertise = data.expertise_areas || data.expertise_domains || [];
        this.displayAuthorExpertise(expertise);
        
        // Display awards
        const awards = data.awards || data.awards_recognition || [];
        this.displayAuthorAwards(awards);
    }

    // AI CONTENT GENERATION METHODS

    generateManipulationFindings(score, techniques, emotionalCount) {
        if (score < 20) {
            return `The article demonstrates minimal manipulation indicators. We found ${emotionalCount} instances of emotional language and ${techniques.length} potential manipulation techniques. The content maintains factual presentation with balanced emotional tone.`;
        } else if (score < 40) {
            return `We detected moderate manipulation indicators including ${emotionalCount} emotionally charged terms and ${techniques.length} rhetorical techniques. The article shows some attempts to influence reader perception through selective framing.`;
        } else if (score < 60) {
            return `Significant manipulation patterns were identified, including ${emotionalCount} emotional triggers and ${techniques.length} manipulation techniques. The article employs persuasive language that may compromise objective analysis.`;
        } else {
            return `High levels of manipulation detected with ${emotionalCount} emotional manipulation instances and ${techniques.length} propaganda techniques. The article heavily employs psychological influence tactics rather than factual argumentation.`;
        }
    }
    
    generateManipulationMeaning(score, riskLevel) {
        if (riskLevel === 'Low') {
            return "This article can be considered reliable in its presentation. The minimal manipulation techniques detected are within normal journalistic bounds. Readers can engage with the content while maintaining standard critical thinking.";
        } else if (riskLevel === 'Medium') {
            return "Readers should approach this article with increased awareness. While not overtly manipulative, the content uses persuasive techniques that may influence interpretation. Cross-reference key claims with other sources.";
        } else {
            return "High caution is advised when reading this article. The manipulation techniques employed suggest an agenda beyond information delivery. Verify all claims independently and be aware of emotional influence attempts.";
        }
    }
    
    generateCredibilityFindings(score, rating, biasLevel, data) {
        const inDatabase = data.in_database ? "is listed in our credibility database" : "is not found in major credibility databases";
        if (score >= 80) {
            return `This source ${inDatabase} with a ${rating} credibility rating. It maintains high journalistic standards, demonstrates consistent factual accuracy, and shows transparent editorial practices. Known bias level: ${biasLevel}.`;
        } else if (score >= 60) {
            return `The source ${inDatabase} with a ${rating} rating. It generally maintains good standards with occasional lapses in accuracy or transparency. Some ${biasLevel} bias has been documented in past reporting.`;
        } else if (score >= 40) {
            return `This source ${inDatabase} showing ${rating} credibility. Mixed track record with documented inaccuracies and ${biasLevel} bias. Editorial standards are inconsistent.`;
        } else {
            return `The source ${inDatabase} with concerning credibility issues. Poor track record of accuracy, significant ${biasLevel} bias, and limited transparency in corrections or sources.`;
        }
    }
    
    generateCredibilityMeaning(score, rating) {
        if (score >= 80) {
            return "You can generally trust information from this source. Their strong track record and professional standards make them reliable for factual reporting, though always maintain healthy skepticism.";
        } else if (score >= 60) {
            return "This source is reasonably reliable but benefits from verification. While generally trustworthy, cross-check important claims with other reputable sources.";
        } else if (score >= 40) {
            return "Exercise caution with this source. Their mixed credibility record means information should be verified through multiple independent sources before accepting as fact.";
        } else {
            return "Significant credibility concerns exist with this source. Information should be treated skeptically and requires thorough verification from established, reputable sources.";
        }
    }
    
    generateBiasFindings(score, lean, dominant) {
        if (score < 30) {
            return `The article maintains strong objectivity with ${lean} political positioning. Minimal bias detected in language choice and source selection. ${dominant !== 'None' ? `Primary bias type: ${dominant}.` : 'Balanced perspective presented.'}`;
        } else if (score < 50) {
            return `Moderate bias detected with ${lean} political lean. The article shows preference in framing and source selection. ${dominant !== 'None' ? `Dominant bias: ${dominant}.` : ''} Some viewpoints may be underrepresented.`;
        } else if (score < 70) {
            return `Significant bias present with clear ${lean} orientation. Strong editorial voice influences presentation. ${dominant !== 'None' ? `Primary bias: ${dominant}.` : ''} Alternative perspectives are marginalized.`;
        } else {
            return `Heavy bias detected with extreme ${lean} positioning. The article functions more as opinion/advocacy than news. ${dominant !== 'None' ? `Dominant bias: ${dominant}.` : ''} Opposing viewpoints are dismissed or misrepresented.`;
        }
    }
    
    generateBiasMeaning(score, objectivity) {
        if (objectivity >= 70) {
            return "The article provides balanced reporting suitable for forming independent opinions. Minor bias present doesn't significantly impact factual accuracy.";
        } else if (objectivity >= 50) {
            return "While containing useful information, be aware of the editorial slant. Consider seeking alternative perspectives to form a complete picture.";
        } else if (objectivity >= 30) {
            return "Strong bias affects the article's reliability as a news source. Treat as perspective/opinion rather than objective reporting. Seek balanced sources for factual information.";
        } else {
            return "Extreme bias makes this more propaganda than journalism. Facts may be distorted or selectively presented. Essential to verify all claims through unbiased sources.";
        }
    }
    
    generateFactCheckFindings(analyzed, verified, claims) {
        if (analyzed === 0) {
            return "No specific factual claims requiring verification were identified. The article consists primarily of opinion, analysis, or unverifiable statements.";
        }
        const accuracy = Math.round((verified / analyzed) * 100);
        if (accuracy >= 90) {
            return `Excellent factual accuracy with ${verified} of ${analyzed} claims verified. The article's factual assertions are well-supported by evidence and consistent with authoritative sources.`;
        } else if (accuracy >= 70) {
            return `Good factual accuracy with ${verified} of ${analyzed} claims verified. Most core facts check out, though some minor claims couldn't be confirmed or contained errors.`;
        } else if (accuracy >= 50) {
            return `Mixed factual accuracy with only ${verified} of ${analyzed} claims verified. Several important claims lack support or contradict established facts.`;
        } else {
            return `Poor factual accuracy with just ${verified} of ${analyzed} claims verified. Numerous factual errors or unsupported claims undermine the article's reliability.`;
        }
    }
    
    generateFactCheckMeaning(score, level) {
        if (level === 'Excellent' || level === 'High') {
            return "The article's facts are reliable and can be trusted for decision-making. The high verification rate indicates careful reporting and fact-checking.";
        } else if (level === 'Good' || level === 'Moderate') {
            return "Core facts appear accurate but some claims need verification. Use the article for general understanding but verify specific claims before citing.";
        } else {
            return "Significant factual issues detected. Do not rely on this article for accurate information without independent verification of all claims.";
        }
    }
    
    generateTransparencyFindings(sources, quotes, score) {
        if (sources >= 10 && quotes >= 5) {
            return `Excellent transparency with ${sources} sources cited and ${quotes} direct quotes. The article clearly attributes information, provides context for claims, and enables verification.`;
        } else if (sources >= 5 && quotes >= 3) {
            return `Good transparency practices with ${sources} sources and ${quotes} quotes. Most claims are attributed though some assertions lack clear sourcing.`;
        } else if (sources >= 2 || quotes >= 1) {
            return `Limited transparency with only ${sources} sources cited and ${quotes} quotes used. Many claims lack attribution, making verification difficult.`;
        } else {
            return `Poor transparency with ${sources} sources and ${quotes} quotes. The article makes numerous unattributed claims and provides little basis for verification.`;
        }
    }
    
    generateTransparencyMeaning(level, score) {
        if (level === 'Very High' || level === 'High') {
            return "Excellent journalistic transparency enables readers to verify claims and understand sources. This level of attribution demonstrates professional reporting standards.";
        } else if (level === 'Moderate') {
            return "Acceptable transparency though improvement needed. Readers can verify some claims but should be aware that not all assertions are properly sourced.";
        } else {
            return "Lack of transparency is concerning. Without proper attribution, readers cannot verify claims or assess source credibility. Treat unsourced claims skeptically.";
        }
    }
    
    generateContentFindings(score, readability, aiInsights, keyPoints) {
        const readabilityText = readability !== 'Unknown' ? `with ${readability} readability score` : '';
        if (score >= 80) {
            return `Excellent content quality ${readabilityText}. Well-structured argumentation, clear writing, and professional presentation. ${aiInsights ? 'AI analysis confirms strong journalistic standards.' : ''}`;
        } else if (score >= 60) {
            return `Good content quality ${readabilityText}. Generally well-written with solid structure, though some sections lack clarity or depth. ${aiInsights ? 'AI identifies areas for improvement in evidence presentation.' : ''}`;
        } else if (score >= 40) {
            return `Moderate content quality ${readabilityText}. Inconsistent writing quality, organizational issues, or superficial treatment of complex topics. ${aiInsights ? 'AI suggests significant structural improvements needed.' : ''}`;
        } else {
            return `Poor content quality ${readabilityText}. Significant issues with clarity, structure, or professionalism. ${aiInsights ? 'AI indicates fundamental journalistic standards not met.' : ''}`;
        }
    }
    
    generateContentMeaning(level, score) {
        if (level === 'Excellent' || level === 'Good') {
            return "The article meets professional journalism standards. Quality writing and structure support effective information delivery and comprehension.";
        } else if (level === 'Fair') {
            return "While readable, the article has quality issues that may affect understanding. Consider these limitations when evaluating the information presented.";
        } else {
            return "Poor content quality undermines credibility. Writing and structural issues suggest rushed or unprofessional work. Verify information through better sources.";
        }
    }

    // HELPER METHODS

    extractAuthorProfiles(data) {
        const profiles = {};
        
        // Check various locations for profile data
        if (data.social_media && typeof data.social_media === 'object') {
            Object.assign(profiles, data.social_media);
        }
        
        // Check individual profile fields
        if (data.linkedin_profile) profiles.linkedin = data.linkedin_profile;
        if (data.twitter_profile) profiles.twitter = data.twitter_profile;
        if (data.wikipedia_page) profiles.wikipedia = data.wikipedia_page;
        if (data.muckrack_profile) profiles.muckrack = data.muckrack_profile;
        if (data.personal_website) profiles.website = data.personal_website;
        
        // Check additional_links
        if (data.additional_links && typeof data.additional_links === 'object') {
            Object.entries(data.additional_links).forEach(([key, value]) => {
                if (value && !profiles[key]) {
                    profiles[key] = value;
                }
            });
        }
        
        return profiles;
    }

    displayPublicationHistory(publications) {
        const section = document.getElementById('publicationSection');
        const list = document.getElementById('publicationList');
        
        if (!section || !list) return;
        
        if (publications && publications.length > 0) {
            section.style.display = 'block';
            list.innerHTML = '';
            
            publications.slice(0, 5).forEach(pub => {
                const pubEl = document.createElement('div');
                pubEl.className = 'publication-item';
                
                const title = pub.title || pub.headline || 'Untitled';
                const date = pub.date || pub.published_date || '';
                const publication = pub.publication || pub.source || '';
                
                pubEl.innerHTML = `
                    <div class="pub-title">${title}</div>
                    <div class="pub-meta">
                        ${publication ? `<span class="pub-source">${publication}</span>` : ''}
                        ${date ? `<span class="pub-date">${this.formatDate(date)}</span>` : ''}
                    </div>
                `;
                
                list.appendChild(pubEl);
            });
        } else {
            section.style.display = 'none';
        }
    }

    updateAuthorCredibilityStyle(score) {
        const scoreEl = document.getElementById('authorCredibilityScore');
        if (!scoreEl) return;
        
        scoreEl.className = 'credibility-score';
        if (score >= 80) {
            scoreEl.classList.add('high');
        } else if (score >= 60) {
            scoreEl.classList.add('good');
        } else if (score >= 40) {
            scoreEl.classList.add('moderate');
        } else if (score > 0) {
            scoreEl.classList.add('low');
        }
    }

    displayAuthorProfiles(profiles) {
        const profilesSection = document.getElementById('authorProfiles');
        const profilesGrid = document.getElementById('profilesGrid');
        
        profilesGrid.innerHTML = '';
        
        const hasProfiles = profiles && Object.values(profiles).some(url => url);
        
        if (hasProfiles) {
            profilesSection.style.display = 'block';
            
            Object.entries(profiles).forEach(([platform, url]) => {
                if (url) {
                    const link = document.createElement('a');
                    link.className = `profile-link ${platform.toLowerCase().replace(/[_\s]/g, '')}`;
                    link.href = url;
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                    link.innerHTML = `<i class="fab fa-${this.getPlatformIcon(platform)}"></i> ${this.formatPlatformName(platform)}`;
                    profilesGrid.appendChild(link);
                }
            });
        } else {
            profilesSection.style.display = 'none';
        }
    }

    displayAuthorExpertise(expertiseList) {
        const expertiseSection = document.getElementById('expertiseSection');
        const expertiseTags = document.getElementById('expertiseTags');
        
        expertiseTags.innerHTML = '';
        
        if (expertiseList && expertiseList.length > 0) {
            expertiseSection.style.display = 'block';
            
            expertiseList.forEach(expertise => {
                const tag = document.createElement('div');
                tag.className = 'expertise-tag';
                tag.textContent = expertise;
                expertiseTags.appendChild(tag);
            });
        } else {
            expertiseSection.style.display = 'none';
        }
    }

    displayAuthorAwards(awardsList) {
        const awardsSection = document.getElementById('awardsSection');
        const awardsList_el = document.getElementById('awardsList');
        
        awardsList_el.innerHTML = '';
        
        if (awardsList && awardsList.length > 0) {
            awardsSection.style.display = 'block';
            
            awardsList.forEach(award => {
                const awardItem = document.createElement('div');
                awardItem.className = 'award-item';
                awardItem.innerHTML = `
                    <div class="award-icon">
                        <i class="fas fa-trophy"></i>
                    </div>
                    <div class="award-text">${award}</div>
                `;
                awardsList_el.appendChild(awardItem);
            });
        } else {
            awardsSection.style.display = 'none';
        }
    }

    displayClaimsList(data) {
        const section = document.getElementById('claimsCheckedSection');
        const list = document.getElementById('verifiedClaimsList');
        
        if (!section || !list) return;
        
        const claims = data.claims || data.verified_claims || data.claim_details || [];
        
        if (claims.length > 0) {
            section.style.display = 'block';
            list.innerHTML = '';
            
            claims.forEach(claim => {
                const claimEl = document.createElement('div');
                claimEl.className = 'claim-item';
                
                const status = claim.verified ? 'verified' : claim.status || 'unverified';
                const icon = status === 'verified' ? 'check-circle' : 
                           status === 'false' ? 'times-circle' : 'question-circle';
                const color = status === 'verified' ? 'green' : 
                            status === 'false' ? 'red' : 'orange';
                
                claimEl.innerHTML = `
                    <div class="claim-status ${status}">
                        <i class="fas fa-${icon}" style="color: ${color}"></i>
                    </div>
                    <div class="claim-text">${claim.text || claim.claim || 'Claim checked'}</div>
                    ${claim.evidence ? `<div class="claim-evidence">${claim.evidence}</div>` : ''}
                `;
                
                list.appendChild(claimEl);
            });
        } else {
            section.style.display = 'none';
        }
    }

    updateBiasMeter(politicalLean, biasScore) {
        const indicator = document.getElementById('biasIndicator');
        if (!indicator) return;
        
        let position = 50;
        const leanMap = {
            'far left': 10, 'left': 30, 'center-left': 40,
            'center': 50, 'center-right': 60, 'right': 70, 'far right': 90
        };
        
        const leanLower = politicalLean.toLowerCase();
        for (const [key, value] of Object.entries(leanMap)) {
            if (leanLower.includes(key)) {
                position = value;
                break;
            }
        }
        
        indicator.style.left = `${position}%`;
        indicator.style.backgroundColor = biasScore >= 70 ? '#ef4444' : 
                                         biasScore >= 50 ? '#f59e0b' : 
                                         biasScore >= 30 ? '#eab308' : '#10b981';
    }

    // Utility functions
    getManipulationRiskLevel(score) {
        const numScore = parseInt(score, 10) || 0;
        if (numScore >= 70) return 'High';
        if (numScore >= 40) return 'Medium';
        return 'Low';
    }

    getQualityLevel(score) {
        const numScore = parseInt(score, 10) || 0;
        if (numScore >= 80) return 'Excellent';
        if (numScore >= 60) return 'Good';
        if (numScore >= 40) return 'Fair';
        return 'Poor';
    }

    getVerificationLevel(score) {
        if (score >= 90) return 'Excellent';
        if (score >= 75) return 'High';
        if (score >= 60) return 'Good';
        if (score >= 40) return 'Moderate';
        return 'Low';
    }

    getTransparencyLevel(score, sources, quotes) {
        if (score >= 80 || (sources >= 10 && quotes >= 5)) return 'Very High';
        if (score >= 60 || (sources >= 5 && quotes >= 3)) return 'High';
        if (score >= 40 || (sources >= 3 && quotes >= 2)) return 'Moderate';
        if (score >= 20 || (sources >= 1 || quotes >= 1)) return 'Low';
        return 'Very Low';
    }

    formatDomainAge(days) {
        if (!days) return 'Unknown';
        const years = Math.floor(days / 365);
        if (years >= 1) {
            return `${years} year${years > 1 ? 's' : ''}`;
        }
        return `${days} days`;
    }

    formatDate(dateStr) {
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric', 
                year: 'numeric' 
            });
        } catch {
            return dateStr;
        }
    }

    getPlatformIcon(platform) {
        const icons = {
            'linkedin': 'linkedin',
            'twitter': 'twitter',
            'wikipedia': 'wikipedia-w',
            'muckrack': 'newspaper',
            'website': 'globe',
            'personal_website': 'globe',
            'scholar': 'graduation-cap'
        };
        const key = platform.toLowerCase().replace(/[_\s]/g, '');
        return icons[key] || 'link';
    }

    formatPlatformName(platform) {
        const names = {
            'linkedin': 'LinkedIn',
            'twitter': 'Twitter',
            'wikipedia': 'Wikipedia',
            'muckrack': 'MuckRack',
            'website': 'Website',
            'personal_website': 'Website',
            'scholar': 'Google Scholar'
        };
        const key = platform.toLowerCase().replace(/[_\s]/g, '');
        return names[key] || platform;
    }

    showDebugInfo(data) {
        const debugInfo = document.getElementById('debugInfo');
        const debugData = document.getElementById('debugData');
        
        if (window.location.hostname === 'localhost' || 
            window.location.hostname.includes('render') ||
            window.location.hostname.includes('onrender')) {
            
            debugData.textContent = JSON.stringify({
                success: data.success,
                trust_score: data.trust_score,
                source: data.source,
                author: data.author,
                detailed_analysis_keys: data.detailed_analysis ? Object.keys(data.detailed_analysis) : [],
                response_time: data.processing_time
            }, null, 2);
            debugInfo.style.display = 'block';
        }
    }

    showResults() {
        this.resultsSection.classList.add('show');
        this.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    setLoading(loading) {
        this.analyzeBtn.disabled = loading;
        if (loading) {
            this.analyzeBtn.innerHTML = '<div class="button-content"><i class="fas fa-spinner fa-spin"></i> Analyzing...</div>';
            document.getElementById('loadingOverlay').classList.add('active');
        } else {
            this.analyzeBtn.innerHTML = '<div class="button-content"><i class="fas fa-search"></i> Analyze Article</div>';
            document.getElementById('loadingOverlay').classList.remove('active');
        }
    }

    showError(message) {
        this.progressContainer.classList.remove('active');
        const errorEl = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        
        if (errorEl && errorText) {
            errorText.textContent = message;
            errorEl.classList.add('active');
            
            // Auto-hide after 8 seconds
            setTimeout(() => {
                errorEl.classList.remove('active');
            }, 8000);
        }
        
        console.error('Analysis error:', message);
    }

    hideError() {
        const errorEl = document.getElementById('errorMessage');
        if (errorEl) {
            errorEl.classList.remove('active');
        }
    }
}

// Global function for toggling service dropdowns
window.toggleServiceDropdown = function(serviceName) {
    const dropdown = document.getElementById(serviceName + 'Dropdown');
    if (dropdown) {
        dropdown.classList.toggle('expanded');
    }
}

// Export for use in other files
window.TruthLensAnalyzer = TruthLensAnalyzer;
