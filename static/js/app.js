/**
 * TruthLens News Analyzer - Main Application JavaScript
 * Handles all analysis functionality, API interactions, and UI updates
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
        
        // Service definitions
        this.services = [
            { id: 'sourceCredibility', name: 'Source Credibility Analysis', icon: 'fa-shield-alt' },
            { id: 'biasDetector', name: 'Bias Detection Analysis', icon: 'fa-balance-scale' },
            { id: 'factChecker', name: 'Fact Checking Analysis', icon: 'fa-check-double' },
            { id: 'transparencyAnalyzer', name: 'Transparency Analysis', icon: 'fa-eye' },
            { id: 'manipulationDetector', name: 'Manipulation Detection', icon: 'fa-exclamation-triangle' },
            { id: 'contentAnalyzer', name: 'Content Analysis', icon: 'fa-file-alt' },
            { id: 'plagiarismDetector', name: 'Plagiarism Detection', icon: 'fa-copy' },
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
            plagiarismDetector: this.getPlagiarismDetectorTemplate(),
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
                    Key Findings
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
            
            <div class="service-findings">
                <div class="findings-title">
                    <i class="fas fa-search"></i>
                    Bias Patterns Detected
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
            
            <div class="service-findings">
                <div class="findings-title">
                    <i class="fas fa-search"></i>
                    Fact Check Results
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
                    Transparency Indicators
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
                    Manipulation Patterns
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
            
            <div class="service-findings">
                <div class="findings-title">
                    <i class="fas fa-search"></i>
                    Content Quality Indicators
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

    getPlagiarismDetectorTemplate() {
        return `
            <div class="service-card-grid">
                <div class="service-metric">
                    <div class="metric-label">Originality Score</div>
                    <div class="metric-value" id="originalityScore">0%</div>
                    <div class="metric-description">Percentage of original content</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Matches Found</div>
                    <div class="metric-value" id="matchesFound">0</div>
                    <div class="metric-description">Number of potential matches detected</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Similarity Score</div>
                    <div class="metric-value" id="similarityScore">0%</div>
                    <div class="metric-description">Percentage of similar content found</div>
                </div>
                <div class="service-metric">
                    <div class="metric-label">Risk Level</div>
                    <div class="metric-value" id="plagiarismRiskLevel">Low</div>
                    <div class="metric-description">Overall plagiarism risk assessment</div>
                </div>
            </div>
            
            <div class="service-findings">
                <div class="findings-title">
                    <i class="fas fa-search"></i>
                    Originality Assessment
                </div>
                <div class="findings-list" id="plagiarismDetectorFindings">
                    <!-- Dynamic findings will be inserted here -->
                </div>
            </div>
            
            <div class="service-interpretation">
                <div class="interpretation-title">Analysis Summary</div>
                <div class="interpretation-text" id="plagiarismDetectorInterpretation">
                    Loading plagiarism detection analysis...
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

    // Continue with rest of methods...
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
        
        // Display each service analysis
        this.displaySourceCredibility(detailed_analysis.source_credibility || {});
        this.displayBiasDetection(detailed_analysis.bias_detector || {});
        this.displayFactChecking(detailed_analysis.fact_checker || {});
        this.displayTransparencyAnalysis(detailed_analysis.transparency_analyzer || {});
        this.displayManipulationDetection(detailed_analysis.manipulation_detector || {});
        this.displayContentAnalysis(detailed_analysis.content_analyzer || {});
        this.displayPlagiarismDetection(detailed_analysis.plagiarism_detector || {});
        this.displayAuthorAnalysis(detailed_analysis.author_analyzer || {}, data.author);
    }

    // Service display methods
    displaySourceCredibility(data) {
        const score = data.score || data.credibility_score || 0;
        const rating = data.credibility || data.credibility_level || 'Unknown';
        const biasLevel = data.bias || data.bias_level || 'Unknown';
        const domainAge = data.domain_age_days ? this.formatDomainAge(data.domain_age_days) : 'Unknown';
        
        document.getElementById('sourceCredibilityScore').textContent = `${score}/100`;
        document.getElementById('sourceCredibilityRating').textContent = rating;
        document.getElementById('sourceBiasLevel').textContent = biasLevel;
        document.getElementById('sourceDomainAge').textContent = domainAge;
        
        // Display findings
        const findings = data.findings || [];
        this.displayFindings('sourceCredibilityFindings', findings);
        
        // Display interpretation
        const interpretation = data.summary || `This source has ${rating.toLowerCase()} credibility with a score of ${score}/100. ${data.in_database ? 'Listed in credibility database.' : 'Not found in credibility database.'} ${biasLevel !== 'Unknown' ? `Known bias: ${biasLevel}.` : ''}`;
        document.getElementById('sourceCredibilityInterpretation').textContent = interpretation;
    }

    displayBiasDetection(data) {
        const biasScore = data.bias_score || data.score || 0;
        const politicalLean = data.dimensions?.political?.label || data.political_lean || 'Neutral';
        const dominantBias = data.dominant_bias || 'None';
        const objectivityScore = data.objectivity_score || (100 - biasScore);
        
        document.getElementById('biasScore').textContent = `${biasScore}/100`;
        document.getElementById('politicalLean').textContent = politicalLean;
        document.getElementById('dominantBias').textContent = dominantBias;
        document.getElementById('objectivityScore').textContent = `${objectivityScore}%`;
        
        // Display findings
        const findings = data.findings || [];
        this.displayFindings('biasDetectorFindings', findings);
        
        // Display interpretation
        const interpretation = data.summary || `Bias analysis detected ${biasScore}% bias with ${politicalLean.toLowerCase()} political lean. ${dominantBias !== 'None' ? `Primary bias type: ${dominantBias}.` : ''} Objectivity score: ${objectivityScore}%.`;
        document.getElementById('biasDetectorInterpretation').textContent = interpretation;
    }

    displayFactChecking(data) {
        const verificationScore = data.score || data.verification_score || 0;
        const claimsAnalyzed = data.claims_found || data.claims_analyzed || 0;
        const claimsVerified = data.claims_checked || data.details?.verified_claims || 0;
        const verificationLevel = data.level || data.verification_level || 'Unknown';
        
        document.getElementById('verificationScore').textContent = `${verificationScore}/100`;
        document.getElementById('claimsAnalyzed').textContent = claimsAnalyzed;
        document.getElementById('claimsVerified').textContent = claimsVerified;
        document.getElementById('verificationLevel').textContent = verificationLevel;
        
        // Display findings
        const findings = data.findings || [];
        this.displayFindings('factCheckerFindings', findings);
        
        // Display interpretation
        const interpretation = data.summary || `Fact checking analysis found ${claimsAnalyzed} verifiable claims, with ${claimsVerified} verified as accurate. Verification level: ${verificationLevel}.`;
        document.getElementById('factCheckerInterpretation').textContent = interpretation;
    }

    displayTransparencyAnalysis(data) {
        const transparencyScore = data.score || data.transparency_score || 0;
        const sourcesCited = data.source_count || data.sources_cited || 0;
        const quotesUsed = data.quote_count || data.quotes_used || 0;
        const disclosureLevel = data.level || data.transparency_level || 'Unknown';
        
        document.getElementById('transparencyScore').textContent = `${transparencyScore}/100`;
        document.getElementById('sourcesCited').textContent = sourcesCited;
        document.getElementById('quotesUsed').textContent = quotesUsed;
        document.getElementById('disclosureLevel').textContent = disclosureLevel;
        
        // Display findings
        const findings = data.findings || [];
        this.displayFindings('transparencyAnalyzerFindings', findings);
        
        // Display interpretation
        const interpretation = data.summary || `Transparency analysis found ${sourcesCited} sources cited and ${quotesUsed} direct quotes. Disclosure level: ${disclosureLevel}. Overall transparency score: ${transparencyScore}/100.`;
        document.getElementById('transparencyAnalyzerInterpretation').textContent = interpretation;
    }

    displayManipulationDetection(data) {
        const manipulationScore = data.score || data.manipulation_score || 0;
        const riskLevel = this.getManipulationRiskLevel(manipulationScore);
        const techniquesFound = data.techniques_found || (data.manipulation_techniques ? data.manipulation_techniques.length : 0) || 0;
        const emotionalLanguage = data.emotional_language_count || data.emotional_words || 0;
        
        document.getElementById('manipulationScore').textContent = `${manipulationScore}/100`;
        document.getElementById('manipulationRiskLevel').textContent = riskLevel;
        document.getElementById('manipulationTechniques').textContent = techniquesFound;
        document.getElementById('emotionalLanguageCount').textContent = emotionalLanguage;
        
        // Display findings
        const findings = data.findings || [];
        this.displayFindings('manipulationDetectorFindings', findings);
        
        // Display interpretation
        const interpretation = data.summary || `Manipulation detection found ${techniquesFound} techniques with ${riskLevel.toLowerCase()} risk level. Detected ${emotionalLanguage} instances of emotional language. Overall manipulation score: ${manipulationScore}/100.`;
        document.getElementById('manipulationDetectorInterpretation').textContent = interpretation;
    }

    displayContentAnalysis(data) {
        const qualityScore = data.score || data.quality_score || 0;
        const qualityLevel = this.getQualityLevel(qualityScore);
        const readability = data.readability || data.readability_score || 'Unknown';
        const structureScore = data.structure_score || data.organization_score || 'Unknown';
        
        document.getElementById('contentQualityScore').textContent = `${qualityScore}/100`;
        document.getElementById('contentQualityLevel').textContent = qualityLevel;
        document.getElementById('contentReadability').textContent = readability;
        document.getElementById('contentStructureScore').textContent = structureScore;
        
        // Display findings
        const findings = data.findings || [];
        this.displayFindings('contentAnalyzerFindings', findings);
        
        // Display interpretation
        const interpretation = data.summary || `Content analysis shows ${qualityLevel.toLowerCase()} quality with ${qualityScore}/100 score. Readability: ${readability}. Structure score: ${structureScore}.`;
        document.getElementById('contentAnalyzerInterpretation').textContent = interpretation;
    }

    displayPlagiarismDetection(data) {
        const originalityScore = data.originality || data.originality_score || 0;
        const matchesFound = data.matches_found || (data.matches ? data.matches.length : 0) || 0;
        const similarityScore = data.similarity_score || data.plagiarism_score || (100 - originalityScore);
        const riskLevel = this.getPlagiarismRiskLevel(originalityScore);
        
        document.getElementById('originalityScore').textContent = `${originalityScore}%`;
        document.getElementById('matchesFound').textContent = matchesFound;
        document.getElementById('similarityScore').textContent = `${similarityScore}%`;
        document.getElementById('plagiarismRiskLevel').textContent = riskLevel;
        
        // Display findings
        const findings = data.findings || [];
        this.displayFindings('plagiarismDetectorFindings', findings);
        
        // Display interpretation
        const interpretation = data.summary || `Plagiarism detection found ${originalityScore}% originality with ${matchesFound} potential matches. Similarity score: ${similarityScore}%. Risk level: ${riskLevel}.`;
        document.getElementById('plagiarismDetectorInterpretation').textContent = interpretation;
    }

    displayAuthorAnalysis(data, fallbackAuthor) {
        console.log('=== Displaying FULL Author Card ===');
        console.log('Author data received:', data);
        
        // Extract comprehensive author information with PROPER data mapping
        let authorName = data.author_name || data.name || fallbackAuthor || 'Unknown';
        let authorScore = data.score || data.credibility_score || data.author_score || 0;
        let authorPosition = data.position || data.title || 'Writer';
        let authorOrganization = data.organization || '';
        let authorBio = data.bio || data.biography || '';
        let hasVerification = data.verified || false;
        
        // Combine position and organization if both exist
        if (authorOrganization && !authorPosition.includes(authorOrganization)) {
            authorPosition = `${authorPosition} at ${authorOrganization}`;
        }
        
        // Update DOM elements
        document.getElementById('authorName').textContent = authorName;
        document.getElementById('authorPosition').textContent = authorPosition;
        document.getElementById('authorCredibilityScore').textContent = authorScore > 0 ? `${authorScore}/100` : 'N/A';
        
        // Update credibility score styling
        const scoreEl = document.getElementById('authorCredibilityScore');
        scoreEl.className = 'credibility-score';
        if (authorScore >= 80) {
            scoreEl.classList.add('high');
        } else if (authorScore >= 60) {
            scoreEl.classList.add('good');
        } else if (authorScore >= 40) {
            scoreEl.classList.add('moderate');
        } else if (authorScore > 0) {
            scoreEl.classList.add('low');
        }
        
        // Extract profiles data - MULTIPLE FORMATS SUPPORTED
        const profiles = {};
        
        // Method 1: Check social_media object
        if (data.social_media && typeof data.social_media === 'object') {
            Object.assign(profiles, data.social_media);
        }
        
        // Method 2: Check individual profile fields
        if (data.linkedin_profile) profiles.linkedin = data.linkedin_profile;
        if (data.twitter_profile) profiles.twitter = data.twitter_profile;
        if (data.wikipedia_page) profiles.wikipedia = data.wikipedia_page;
        if (data.muckrack_profile) profiles.muckrack = data.muckrack_profile;
        if (data.personal_website) profiles.website = data.personal_website;
        
        // Method 3: Check additional_links
        if (data.additional_links && typeof data.additional_links === 'object') {
            Object.entries(data.additional_links).forEach(([key, value]) => {
                if (value && !profiles[key]) {
                    profiles[key] = value;
                }
            });
        }
        
        // Update stats with real counts
        const profilesCount = Object.values(profiles).filter(url => url).length;
        const articleCount = data.article_count || data.publishing_history?.length || 0;
        const awardsCount = data.awards?.length || data.awards_recognition?.length || 0;
        
        document.getElementById('articleCount').textContent = articleCount;
        document.getElementById('profilesCount').textContent = profilesCount;
        document.getElementById('awardsCount').textContent = awardsCount;
        
        // Handle biography
        const bioSection = document.getElementById('authorBio');
        const bioText = document.getElementById('authorBioText');
        if (authorBio && authorBio.trim()) {
            bioSection.style.display = 'block';
            bioText.textContent = authorBio;
        } else {
            bioSection.style.display = 'none';
        }
        
        // Handle verification badge
        const verificationBadge = document.getElementById('verificationBadge');
        if (hasVerification) {
            verificationBadge.style.display = 'flex';
        } else {
            verificationBadge.style.display = 'none';
        }
        
        // Handle professional profiles with ALL data
        this.displayAuthorProfiles(profiles);
        
        // Handle expertise areas
        const expertise = data.expertise_areas || data.expertise_domains || [];
        this.displayAuthorExpertise(expertise);
        
        // Handle awards
        const awards = data.awards || data.awards_recognition || [];
        this.displayAuthorAwards(awards);
        
        console.log('Author card updated with full rich functionality');
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

    displayFindings(containerId, findings) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        
        if (!findings || findings.length === 0) {
            container.innerHTML = '<div class="finding-item finding-neutral"><div class="finding-icon"><i class="fas fa-info"></i></div><div class="finding-content"><div class="finding-text">No specific findings available</div></div></div>';
            return;
        }
        
        findings.slice(0, 5).forEach(finding => {
            const findingEl = document.createElement('div');
            const severity = finding.severity || finding.type || 'neutral';
            const icon = this.getFindingIcon(severity);
            
            findingEl.className = `finding-item finding-${severity}`;
            findingEl.innerHTML = `
                <div class="finding-icon">${icon}</div>
                <div class="finding-content">
                    <div class="finding-text">${finding.text || finding.finding || finding.message || 'Finding available'}</div>
                    ${finding.explanation ? `<div class="finding-explanation">${finding.explanation}</div>` : ''}
                </div>
            `;
            
            container.appendChild(findingEl);
        });
    }

    // Utility functions
    getFindingIcon(severity) {
        switch (severity) {
            case 'positive':
            case 'low':
                return '<i class="fas fa-check"></i>';
            case 'warning':
            case 'medium':
                return '<i class="fas fa-exclamation"></i>';
            case 'negative':
            case 'high':
                return '<i class="fas fa-times"></i>';
            default:
                return '<i class="fas fa-info"></i>';
        }
    }

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

    getPlagiarismRiskLevel(originalityScore) {
        const numScore = parseInt(originalityScore, 10) || 0;
        if (numScore >= 80) return 'Low';
        if (numScore >= 60) return 'Medium';
        return 'High';
    }

    formatDomainAge(days) {
        if (!days) return 'Unknown';
        const years = Math.floor(days / 365);
        if (years >= 1) {
            return `${years} year${years > 1 ? 's' : ''}`;
        }
        return `${days} days`;
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
            'm
