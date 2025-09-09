/**
 * TruthLens Service Templates - ENHANCED VERSION WITH SOURCE RANKINGS
 * Date: September 7, 2025
 * Last Updated: December 18, 2024
 * 
 * ENHANCEMENTS:
 * - Added Source Credibility Rankings Chart (Top 10 + Current Source)
 * - Complete author intelligence display
 * - Trust indicators and red flags
 * - AI assessment display
 * - Social profile links
 * - Biography section
 * - Can Trust determination
 */

window.ServiceTemplates = {
    
    // Source database for rankings (top sources with scores)
    sourceRankings: [
        { name: 'Reuters', score: 95 },
        { name: 'Associated Press', score: 94 },
        { name: 'BBC', score: 92 },
        { name: 'NPR', score: 90 },
        { name: 'ProPublica', score: 89 },
        { name: 'The Guardian', score: 85 },
        { name: 'The New York Times', score: 83 },
        { name: 'The Washington Post', score: 82 },
        { name: 'The Wall Street Journal', score: 80 },
        { name: 'The Economist', score: 78 },
        { name: 'USA Today', score: 75 },
        { name: 'CBS News', score: 73 },
        { name: 'ABC News', score: 72 },
        { name: 'NBC News', score: 71 },
        { name: 'CNN', score: 65 },
        { name: 'Fox News', score: 62 },
        { name: 'MSNBC', score: 60 },
        { name: 'HuffPost', score: 55 },
        { name: 'Vox', score: 52 },
        { name: 'BuzzFeed', score: 45 },
        { name: 'Daily Mail', score: 38 },
        { name: 'New York Post', score: 35 },
        { name: 'Breitbart', score: 25 },
        { name: 'InfoWars', score: 10 }
    ],
    
    getTemplate(serviceId) {
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
    },

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
            
            <!-- NEW: Source Rankings Chart -->
            <div class="source-rankings-compact" id="sourceRankingsChart" style="display: none;">
                <div class="rankings-header-compact">
                    <h3 class="rankings-title-compact">
                        <i class="fas fa-trophy"></i>
                        Source Credibility Rankings
                    </h3>
                </div>
                <div class="rankings-chart-compact" id="rankingsChartContent">
                    <!-- Chart items will be inserted here dynamically -->
                </div>
            </div>
            
            <div class="service-findings">
                <div class="findings-title">
                    <i class="fas fa-search"></i>
                    Analysis Details
                </div>
                <div class="findings-list" id="sourceCredibilityFindings"></div>
            </div>
            
            <div class="service-interpretation">
                <div class="interpretation-title">Analysis Summary</div>
                <div class="interpretation-text" id="sourceCredibilityInterpretation">
                    Loading source credibility analysis...
                </div>
            </div>
        `;
    },

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
                <div class="findings-list" id="biasDetectorFindings"></div>
            </div>
            
            <div class="service-interpretation">
                <div class="interpretation-title">Analysis Summary</div>
                <div class="interpretation-text" id="biasDetectorInterpretation">
                    Loading bias detection analysis...
                </div>
            </div>
        `;
    },

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
            
            <div class="claims-checked-section" id="claimsCheckedSection" style="display: none;">
                <h4 class="section-title">
                    <i class="fas fa-list-check"></i>
                    Claims Verified
                </h4>
                <div class="claims-list" id="verifiedClaimsList"></div>
            </div>
            
            <div class="service-findings">
                <div class="findings-title">
                    <i class="fas fa-search"></i>
                    Analysis Details
                </div>
                <div class="findings-list" id="factCheckerFindings"></div>
            </div>
            
            <div class="service-interpretation">
                <div class="interpretation-title">Analysis Summary</div>
                <div class="interpretation-text" id="factCheckerInterpretation">
                    Loading fact checking analysis...
                </div>
            </div>
        `;
    },

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
                <div class="findings-list" id="transparencyAnalyzerFindings"></div>
            </div>
            
            <div class="service-interpretation">
                <div class="interpretation-title">Analysis Summary</div>
                <div class="interpretation-text" id="transparencyAnalyzerInterpretation">
                    Loading transparency analysis...
                </div>
            </div>
        `;
    },

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
                <div class="findings-list" id="manipulationDetectorFindings"></div>
            </div>
            
            <div class="service-interpretation">
                <div class="interpretation-title">Analysis Summary</div>
                <div class="interpretation-text" id="manipulationDetectorInterpretation">
                    Loading manipulation detection analysis...
                </div>
            </div>
        `;
    },

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
            
            <div class="ai-enhancement-section" id="aiEnhancementSection" style="display: none;">
                <h4 class="section-title">
                    <i class="fas fa-robot"></i>
                    AI-Enhanced Analysis
                </h4>
                <div class="ai-summary" id="aiSummaryContent"></div>
            </div>
            
            <div class="service-findings">
                <div class="findings-title">
                    <i class="fas fa-search"></i>
                    Analysis Details
                </div>
                <div class="findings-list" id="contentAnalyzerFindings"></div>
            </div>
            
            <div class="service-interpretation">
                <div class="interpretation-title">Analysis Summary</div>
                <div class="interpretation-text" id="contentAnalyzerInterpretation">
                    Loading content analysis...
                </div>
            </div>
        `;
    },

    getAuthorAnalysisTemplate() {
        return `
            <!-- Trust Decision Box -->
            <div class="author-trust-decision" id="authorTrustDecision" style="display: none;">
                <div class="trust-indicator" id="trustIndicator">
                    <i class="fas fa-shield-alt"></i>
                    <span id="trustDecisionText">Can Trust: Unknown</span>
                </div>
                <div class="trust-reasoning" id="trustReasoning"></div>
            </div>

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

            <!-- AI Assessment -->
            <div class="ai-assessment-section" id="aiAssessmentSection" style="display: none;">
                <h4 class="author-section-title">
                    <i class="fas fa-robot"></i>
                    AI Assessment
                </h4>
                <div class="ai-assessment-text" id="aiAssessmentText"></div>
            </div>

            <!-- Trust Indicators -->
            <div class="trust-indicators-section" id="trustIndicatorsSection" style="display: none;">
                <h4 class="author-section-title">
                    <i class="fas fa-check-circle" style="color: #10b981;"></i>
                    Trust Indicators
                </h4>
                <ul class="trust-indicators-list" id="trustIndicatorsList"></ul>
            </div>

            <!-- Red Flags -->
            <div class="red-flags-section" id="redFlagsSection" style="display: none;">
                <h4 class="author-section-title">
                    <i class="fas fa-exclamation-triangle" style="color: #ef4444;"></i>
                    Concerns
                </h4>
                <ul class="red-flags-list" id="redFlagsList"></ul>
            </div>

            <div class="author-profiles" id="authorProfiles" style="display: none;">
                <h4 class="author-section-title">
                    <i class="fas fa-link"></i>
                    Professional Profiles
                </h4>
                <div class="profiles-grid" id="profilesGrid"></div>
            </div>

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

            <div class="author-bio" id="authorBio" style="display: none;">
                <h4 class="author-section-title">
                    <i class="fas fa-user-circle"></i>
                    Biography
                </h4>
                <p class="author-bio-text" id="authorBioText"></p>
            </div>

            <div class="expertise-section" id="expertiseSection" style="display: none;">
                <h4 class="author-section-title">
                    <i class="fas fa-brain"></i>
                    Areas of Expertise
                </h4>
                <div class="expertise-tags" id="expertiseTags"></div>
            </div>

            <div class="publication-section" id="publicationSection" style="display: none;">
                <h4 class="author-section-title">
                    <i class="fas fa-newspaper"></i>
                    Recent Publications
                </h4>
                <div class="publication-list" id="publicationList"></div>
            </div>

            <div class="awards-section" id="awardsSection" style="display: none;">
                <h4 class="author-section-title">
                    <i class="fas fa-trophy"></i>
                    Awards & Recognition
                </h4>
                <div class="awards-list" id="awardsList"></div>
            </div>
        `;
    },

    // Display methods for all services
    displayAllAnalyses(data, analyzer) {
        console.log('=== Displaying All Service Analyses ===');
        console.log('Data received:', data);
        
        const detailed_analysis = data.detailed_analysis || {};
        
        // Hide plagiarism detector
        const plagiarismDropdown = document.getElementById('plagiarismDetectorDropdown');
        if (plagiarismDropdown) {
            plagiarismDropdown.style.display = 'none';
        }
        
        // Display each service
        this.displaySourceCredibility(detailed_analysis.source_credibility || {}, analyzer);
        this.displayBiasDetection(detailed_analysis.bias_detector || {}, analyzer);
        this.displayFactChecking(detailed_analysis.fact_checker || {}, analyzer);
        this.displayTransparencyAnalysis(detailed_analysis.transparency_analyzer || {}, analyzer);
        this.displayManipulationDetection(detailed_analysis.manipulation_detector || {}, analyzer);
        this.displayContentAnalysis(detailed_analysis.content_analyzer || {}, detailed_analysis.openai_enhancer || {}, analyzer);
        this.displayAuthorAnalysis(detailed_analysis.author_analyzer || {}, data.author, analyzer);
    },

    // Enhanced displaySourceCredibility with rankings chart
    displaySourceCredibility(data, analyzer) {
        const score = data.score || data.credibility_score || 0;
        const rating = data.credibility || data.credibility_level || 'Unknown';
        const biasLevel = data.bias || data.bias_level || 'Unknown';
        const domainAge = data.domain_age_days ? this.formatDomainAge(data.domain_age_days) : 'Unknown';
        
        // Get the current source name
        const currentSourceName = data.source_name || data.source || 'Unknown Source';
        
        const whatWeLooked = data.analysis?.what_we_looked || 
            "We evaluated the news source's historical accuracy, editorial standards, ownership transparency, correction policies, and journalistic practices.";
        
        const whatWeFound = data.analysis?.what_we_found || this.generateCredibilityFindings(score, rating, biasLevel, data);
        const whatItMeans = data.analysis?.what_it_means || this.generateCredibilityMeaning(score, rating);
        
        document.getElementById('sourceCredibilityScore').textContent = `${score}/100`;
        document.getElementById('sourceCredibilityRating').textContent = rating;
        document.getElementById('sourceBiasLevel').textContent = biasLevel;
        document.getElementById('sourceDomainAge').textContent = domainAge;
        
        // Display the rankings chart
        this.displaySourceRankingsChart(currentSourceName, score);
        
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
    },

    // NEW METHOD: Display Source Rankings Chart
    displaySourceRankingsChart(currentSourceName, currentScore) {
        const chartContainer = document.getElementById('sourceRankingsChart');
        const chartContent = document.getElementById('rankingsChartContent');
        
        if (!chartContainer || !chartContent) return;
        
        // Show the chart
        chartContainer.style.display = 'block';
        chartContent.innerHTML = '';
        
        // Get top 10 sources
        let topSources = [...this.sourceRankings]
            .sort((a, b) => b.score - a.score)
            .slice(0, 10);
        
        // Check if current source is in top 10
        const currentInTop = topSources.find(s => 
            s.name.toLowerCase() === currentSourceName.toLowerCase() ||
            currentSourceName.toLowerCase().includes(s.name.toLowerCase())
        );
        
        // If current source isn't in top 10, add it
        if (!currentInTop && currentSourceName !== 'Unknown Source') {
            // Find where it should be inserted based on score
            let insertIndex = topSources.findIndex(s => s.score < currentScore);
            if (insertIndex === -1) insertIndex = topSources.length;
            
            // If it belongs in top 10, replace the last item
            if (insertIndex < 10) {
                topSources.splice(insertIndex, 0, {
                    name: currentSourceName,
                    score: currentScore,
                    isCurrent: true
                });
                topSources = topSources.slice(0, 10);
            } else {
                // Add at the end as 11th item
                topSources.push({
                    name: currentSourceName,
                    score: currentScore,
                    isCurrent: true
                });
            }
        } else if (currentInTop) {
            // Mark the current source
            currentInTop.isCurrent = true;
        }
        
        // Create chart items
        topSources.forEach((source, index) => {
            const rankItem = document.createElement('div');
            rankItem.className = 'ranking-item-compact';
            
            // Determine trust level for coloring
            let trustLevel = '';
            if (source.score >= 80) trustLevel = 'highly-trusted';
            else if (source.score >= 60) trustLevel = 'trusted';
            else if (source.score >= 40) trustLevel = 'moderate';
            else trustLevel = 'low';
            
            rankItem.classList.add(trustLevel);
            
            // Add current source class if applicable
            if (source.isCurrent) {
                rankItem.classList.add('current-source');
            }
            
            rankItem.innerHTML = `
                <span class="rank-number">${index + 1}</span>
                <span class="source-name-compact">${source.name}</span>
                <div class="score-bar-compact" style="flex: 1; margin: 0 15px;">
                    <div class="score-fill" style="width: ${source.score}%"></div>
                </div>
                <span class="score-value">${source.score}</span>
                ${source.isCurrent ? '<span class="current-badge">CURRENT</span>' : ''}
            `;
            
            chartContent.appendChild(rankItem);
            
            // Animate in
            setTimeout(() => {
                rankItem.classList.add('animate-in');
            }, index * 50);
        });
    },

    displayBiasDetection(data, analyzer) {
        const biasScore = data.bias_score || data.score || 0;
        const politicalLean = data.dimensions?.political?.label || data.political_lean || 'Neutral';
        const dominantBias = data.dominant_bias || 'None';
        const objectivityScore = data.objectivity_score !== undefined ? data.objectivity_score : (100 - biasScore);
        
        const whatWeLooked = data.analysis?.what_we_looked || 
            "We analyzed language patterns, source selection, framing techniques, and narrative balance.";
        
        const whatWeFound = data.analysis?.what_we_found || this.generateBiasFindings(biasScore, politicalLean, dominantBias);
        const whatItMeans = data.analysis?.what_it_means || this.generateBiasMeaning(biasScore, objectivityScore);
        
        document.getElementById('biasScore').textContent = `${biasScore}/100`;
        document.getElementById('politicalLean').textContent = politicalLean;
        document.getElementById('dominantBias').textContent = dominantBias;
        document.getElementById('objectivityScore').textContent = `${objectivityScore}%`;
        
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
    },

    // [Keep all other display methods unchanged from original...]
    displayFactChecking(data, analyzer) {
        const claimsAnalyzed = data.claims_found || data.claims_analyzed || 0;
        const claimsVerified = data.claims_verified || 0;
        
        let verificationScore = 0;
        if (claimsAnalyzed > 0) {
            verificationScore = Math.round((claimsVerified / claimsAnalyzed) * 100);
        } else {
            verificationScore = data.score || 0;
        }
        
        const verificationLevel = this.getVerificationLevel(verificationScore);
        
        const whatWeLooked = data.analysis?.what_we_looked || 
            "We identified and examined verifiable claims in the article.";
        
        const whatWeFound = data.analysis?.what_we_found || this.generateFactCheckFindings(claimsAnalyzed, claimsVerified, data.claims);
        const whatItMeans = data.analysis?.what_it_means || this.generateFactCheckMeaning(verificationScore, verificationLevel);
        
        document.getElementById('verificationScore').textContent = `${verificationScore}/100`;
        document.getElementById('claimsAnalyzed').textContent = claimsAnalyzed;
        document.getElementById('claimsVerified').textContent = claimsVerified;
        document.getElementById('verificationLevel').textContent = verificationLevel;
        
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
    },

    displayTransparencyAnalysis(data, analyzer) {
        const sourcesCited = data.source_count || data.sources_cited || 0;
        const quotesUsed = data.quote_count || data.quotes_used || 0;
        
        let transparencyScore;
        if (sourcesCited > 0 || quotesUsed > 0) {
            const sourceScore = Math.min(sourcesCited * 8, 50);
            const quoteScore = Math.min(quotesUsed * 10, 50);
            transparencyScore = Math.min(sourceScore + quoteScore, 100);
        } else {
            transparencyScore = data.score || data.transparency_score || 0;
        }
        
        const disclosureLevel = this.getTransparencyLevel(transparencyScore, sourcesCited, quotesUsed);
        
        const whatWeLooked = data.analysis?.what_we_looked || 
            "We examined source attribution, quote usage, data transparency, and methodology explanations.";
        
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
    },

    displayManipulationDetection(data, analyzer) {
        const manipulationScore = data.score || data.manipulation_score || 0;
        const riskLevel = this.getManipulationRiskLevel(manipulationScore);
        const techniques = data.manipulation_techniques || [];
        const emotionalCount = data.emotional_language_count || data.emotional_words || 0;
        
        const whatWeLooked = data.analysis?.what_we_looked || 
            "We examined the article for manipulation techniques including emotional language patterns and logical fallacies.";
        
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
    },

    displayContentAnalysis(contentData, openaiData, analyzer) {
        const qualityScore = contentData.score || contentData.quality_score || 0;
        const qualityLevel = this.getQualityLevel(qualityScore);
        const readability = contentData.readability || contentData.readability_score || 'Unknown';
        const structureScore = contentData.structure_score || contentData.organization_score || 'Unknown';
        
        const aiInsights = openaiData?.summary || openaiData?.enhanced_summary || '';
        const keyPoints = openaiData?.key_points || [];
        
        const whatWeLooked = contentData.analysis?.what_we_looked || 
            "We evaluated writing quality, logical structure, evidence presentation, and journalistic standards.";
        
        const whatWeFound = contentData.analysis?.what_we_found || this.generateContentFindings(qualityScore, readability, aiInsights, keyPoints);
        const whatItMeans = contentData.analysis?.what_it_means || this.generateContentMeaning(qualityLevel, qualityScore);
        
        document.getElementById('contentQualityScore').textContent = `${qualityScore}/100`;
        document.getElementById('contentQualityLevel').textContent = qualityLevel;
        document.getElementById('contentReadability').textContent = readability;
        document.getElementById('contentStructureScore').textContent = structureScore;
        
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
    },

    // [Keep all other methods unchanged from original...]
    displayAuthorAnalysis(data, fallbackAuthor, analyzer) {
        console.log('=== Displaying Enhanced Author Analysis ===');
        console.log('Author data:', data);
        
        // Basic info
        const authorName = data.author_name || data.name || fallbackAuthor || 'Unknown';
        const authorScore = data.combined_credibility_score || data.credibility_score || data.score || 0;
        const authorPosition = data.position || 'Writer';
        const authorOrganization = data.organization || data.domain || '';
        const authorBio = data.biography || data.bio || '';
        
        const fullPosition = authorOrganization && !authorPosition.toLowerCase().includes(authorOrganization.toLowerCase()) 
            ? `${authorPosition} at ${authorOrganization}` 
            : authorPosition;
        
        // Display basic info
        document.getElementById('authorName').textContent = authorName;
        document.getElementById('authorPosition').textContent = fullPosition;
        document.getElementById('authorCredibilityScore').textContent = authorScore > 0 ? `${authorScore}/100` : 'N/A';
        
        this.updateAuthorCredibilityStyle(authorScore);
        
        // Display Trust Decision (NEW)
        const canTrust = data.can_trust !== undefined ? data.can_trust : (authorScore >= 40);
        const trustReasoning = data.trust_reasoning || this.generateTrustReasoning(authorScore, data);
        
        const trustDecisionEl = document.getElementById('authorTrustDecision');
        const trustIndicatorEl = document.getElementById('trustIndicator');
        const trustDecisionTextEl = document.getElementById('trustDecisionText');
        const trustReasoningEl = document.getElementById('trustReasoning');
        
        if (trustDecisionEl) {
            trustDecisionEl.style.display = 'block';
            
            if (canTrust) {
                trustIndicatorEl.className = 'trust-indicator trust-yes';
                trustDecisionTextEl.textContent = 'Can Trust: YES';
            } else {
                trustIndicatorEl.className = 'trust-indicator trust-no';
                trustDecisionTextEl.textContent = 'Can Trust: NO';
            }
            
            trustReasoningEl.textContent = trustReasoning;
        }
        
        // Display AI Assessment (NEW)
        const aiAssessment = data.ai_assessment || '';
        if (aiAssessment) {
            const aiSection = document.getElementById('aiAssessmentSection');
            const aiText = document.getElementById('aiAssessmentText');
            if (aiSection && aiText) {
                aiSection.style.display = 'block';
                aiText.textContent = aiAssessment;
            }
        }
        
        // Display Trust Indicators (NEW)
        const trustIndicators = data.trust_indicators || [];
        if (trustIndicators.length > 0) {
            const indicatorsSection = document.getElementById('trustIndicatorsSection');
            const indicatorsList = document.getElementById('trustIndicatorsList');
            if (indicatorsSection && indicatorsList) {
                indicatorsSection.style.display = 'block';
                indicatorsList.innerHTML = trustIndicators
                    .map(indicator => `<li><i class="fas fa-check"></i> ${indicator}</li>`)
                    .join('');
            }
        }
        
        // Display Red Flags (NEW)
        const redFlags = data.red_flags || data.potential_issues || [];
        if (redFlags.length > 0) {
            const flagsSection = document.getElementById('redFlagsSection');
            const flagsList = document.getElementById('redFlagsList');
            if (flagsSection && flagsList) {
                flagsSection.style.display = 'block';
                flagsList.innerHTML = redFlags
                    .map(flag => `<li><i class="fas fa-times"></i> ${flag}</li>`)
                    .join('');
            }
        }
        
        // Display Social Profiles with Links (ENHANCED)
        const socialProfiles = data.social_profiles || [];
        const professionalLinks = data.professional_links || [];
        this.displayEnhancedProfiles(socialProfiles, professionalLinks);
        
        // Stats
        const articleCount = data.articles_found || data.article_count || 0;
        const profilesCount = socialProfiles.length || 0;
        const awardsCount = (data.awards || []).length || 0;
        
        document.getElementById('articleCount').textContent = articleCount;
        document.getElementById('profilesCount').textContent = profilesCount;
        document.getElementById('awardsCount').textContent = awardsCount;
        
        // Biography
        if (authorBio && authorBio.trim()) {
            document.getElementById('authorBio').style.display = 'block';
            document.getElementById('authorBioText').textContent = authorBio;
        }
        
        // Expertise
        const expertise = data.expertise_areas || [];
        this.displayAuthorExpertise(expertise);
        
        // Recent Articles (ENHANCED)
        const recentArticles = data.recent_articles || [];
        this.displayEnhancedPublications(recentArticles);
        
        // Awards
        const awards = data.awards || [];
        this.displayAuthorAwards(awards);
    },

    // [Keep all helper methods unchanged from original...]
    generateTrustReasoning(score, data) {
        if (score >= 80) {
            return "Highly credible journalist with extensive track record and verification.";
        } else if (score >= 60) {
            return "Generally trustworthy author with good publication history.";
        } else if (score >= 40) {
            return "Mixed credibility indicators. Verify important claims independently.";
        } else {
            return "Limited credibility information available. Exercise caution.";
        }
    },

    displayEnhancedProfiles(socialProfiles, professionalLinks) {
        const profilesSection = document.getElementById('authorProfiles');
        const profilesGrid = document.getElementById('profilesGrid');
        
        if (!profilesGrid) return;
        profilesGrid.innerHTML = '';
        
        const allProfiles = [];
        
        // Add social profiles
        if (socialProfiles && socialProfiles.length > 0) {
            socialProfiles.forEach(profile => {
                if (profile.url) {
                    allProfiles.push({
                        platform: profile.platform,
                        url: profile.url,
                        verified: profile.verified
                    });
                }
            });
        }
        
        // Add professional links
        if (professionalLinks && professionalLinks.length > 0) {
            professionalLinks.forEach(url => {
                const platform = this.detectPlatformFromUrl(url);
                allProfiles.push({
                    platform: platform,
                    url: url,
                    verified: false
                });
            });
        }
        
        if (allProfiles.length > 0) {
            if (profilesSection) profilesSection.style.display = 'block';
            
            allProfiles.forEach(profile => {
                const link = document.createElement('a');
                link.className = `profile-link ${profile.platform.toLowerCase().replace(/[^a-z]/g, '')}`;
                link.href = profile.url;
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
                
                const icon = this.getPlatformIcon(profile.platform);
                link.innerHTML = `
                    <i class="fab fa-${icon}"></i> 
                    ${profile.platform}
                    ${profile.verified ? '<span class="verified-badge">✓</span>' : ''}
                `;
                
                profilesGrid.appendChild(link);
            });
        } else {
            if (profilesSection) profilesSection.style.display = 'none';
        }
    },

    displayEnhancedPublications(articles) {
        const section = document.getElementById('publicationSection');
        const list = document.getElementById('publicationList');
        
        if (!section || !list) return;
        
        if (articles && articles.length > 0) {
            section.style.display = 'block';
            list.innerHTML = '';
            
            articles.slice(0, 5).forEach(article => {
                const pubEl = document.createElement('div');
                pubEl.className = 'publication-item';
                
                const title = article.title || 'Untitled';
                const source = article.source || '';
                const date = article.date || '';
                const url = article.url || '';
                
                pubEl.innerHTML = `
                    ${url ? `<a href="${url}" target="_blank" class="pub-title-link">` : '<div class="pub-title">'}
                        ${title}
                    ${url ? '</a>' : '</div>'}
                    <div class="pub-meta">
                        ${source ? `<span class="pub-source">${source}</span>` : ''}
                        ${date ? `<span class="pub-date">${this.formatDate(date)}</span>` : ''}
                    </div>
                `;
                
                list.appendChild(pubEl);
            });
        } else {
            section.style.display = 'none';
        }
    },

    detectPlatformFromUrl(url) {
        if (url.includes('linkedin')) return 'LinkedIn';
        if (url.includes('twitter') || url.includes('x.com')) return 'Twitter/X';
        if (url.includes('wikipedia')) return 'Wikipedia';
        if (url.includes('muckrack')) return 'Muck Rack';
        if (url.includes('facebook')) return 'Facebook';
        return 'Website';
    },

    updateAuthorCredibilityStyle(score) {
        const scoreEl = document.getElementById('authorCredibilityScore');
        if (!scoreEl) return;
        
        scoreEl.className = 'credibility-score';
        if (score >= 80) scoreEl.classList.add('high');
        else if (score >= 60) scoreEl.classList.add('good');
        else if (score >= 40) scoreEl.classList.add('moderate');
        else if (score > 0) scoreEl.classList.add('low');
    },

    displayAuthorExpertise(expertiseList) {
        const section = document.getElementById('expertiseSection');
        const tags = document.getElementById('expertiseTags');
        
        if (!tags) return;
        tags.innerHTML = '';
        
        if (expertiseList && expertiseList.length > 0) {
            if (section) section.style.display = 'block';
            
            expertiseList.forEach(expertise => {
                const tag = document.createElement('div');
                tag.className = 'expertise-tag';
                tag.textContent = expertise;
                tags.appendChild(tag);
            });
        } else {
            if (section) section.style.display = 'none';
        }
    },

    displayAuthorAwards(awardsList) {
        const section = document.getElementById('awardsSection');
        const list = document.getElementById('awardsList');
        
        if (!list) return;
        list.innerHTML = '';
        
        if (awardsList && awardsList.length > 0) {
            if (section) section.style.display = 'block';
            
            awardsList.forEach(award => {
                const item = document.createElement('div');
                item.className = 'award-item';
                item.innerHTML = `
                    <div class="award-icon"><i class="fas fa-trophy"></i></div>
                    <div class="award-text">${award}</div>
                `;
                list.appendChild(item);
            });
        } else {
            if (section) section.style.display = 'none';
        }
    },

    getPlatformIcon(platform) {
        const icons = {
            'linkedin': 'linkedin',
            'twitter': 'twitter',
            'twitter/x': 'twitter',
            'wikipedia': 'wikipedia-w',
            'muck rack': 'newspaper',
            'muckrack': 'newspaper',
            'facebook': 'facebook',
            'website': 'globe'
        };
        return icons[platform.toLowerCase()] || 'link';
    },

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
    },

    generateCredibilityFindings(score, rating, biasLevel, data) {
        const inDatabase = data.in_database ? "is listed in our credibility database" : "is not found in major credibility databases";
        if (score >= 80) {
            return `This source ${inDatabase} with a ${rating} credibility rating. It maintains high journalistic standards with ${biasLevel} bias level.`;
        } else if (score >= 60) {
            return `The source ${inDatabase} with a ${rating} rating. Generally maintains good standards with ${biasLevel} bias documented.`;
        } else if (score >= 40) {
            return `This source ${inDatabase} showing ${rating} credibility. Mixed track record with ${biasLevel} bias.`;
        } else {
            return `The source ${inDatabase} with concerning credibility issues. Significant ${biasLevel} bias detected.`;
        }
    },

    generateCredibilityMeaning(score, rating) {
        if (score >= 80) return "You can generally trust information from this source.";
        if (score >= 60) return "This source is reasonably reliable but verify important claims.";
        if (score >= 40) return "Exercise caution with this source.";
        return "Significant credibility concerns exist with this source.";
    },

    generateBiasFindings(score, lean, dominant) {
        if (score < 30) return `Minimal bias detected with ${lean} political positioning.`;
        if (score < 50) return `Moderate bias with ${lean} political lean detected.`;
        if (score < 70) return `Significant bias with clear ${lean} orientation.`;
        return `Heavy bias with extreme ${lean} positioning detected.`;
    },

    generateBiasMeaning(score, objectivity) {
        if (objectivity >= 70) return "Balanced reporting suitable for forming independent opinions.";
        if (objectivity >= 50) return "Be aware of editorial slant when reading.";
        return "Strong bias affects reliability as news source.";
    },

    generateFactCheckFindings(analyzed, verified, claims) {
        if (analyzed === 0) return "No specific factual claims requiring verification were identified.";
        const accuracy = Math.round((verified / analyzed) * 100);
        return `${verified} of ${analyzed} claims verified (${accuracy}% accuracy).`;
    },

    generateFactCheckMeaning(score, level) {
        if (score >= 75) return "Facts are reliable and can be trusted.";
        if (score >= 50) return "Core facts appear accurate but verify specifics.";
        return "Significant factual issues detected.";
    },

    generateTransparencyFindings(sources, quotes, score) {
        if (sources >= 10 && quotes >= 5) return `Excellent transparency with ${sources} sources and ${quotes} quotes.`;
        if (sources >= 5 && quotes >= 3) return `Good transparency with ${sources} sources and ${quotes} quotes.`;
        return `Limited transparency with ${sources} sources and ${quotes} quotes.`;
    },

    generateTransparencyMeaning(level, score) {
        if (score >= 70) return "Excellent transparency enables verification.";
        if (score >= 40) return "Acceptable transparency though improvement needed.";
        return "Lack of transparency is concerning.";
    },

    generateManipulationFindings(score, techniques, emotionalCount) {
        if (score < 20) return `Minimal manipulation with ${emotionalCount} emotional terms.`;
        if (score < 40) return `Moderate manipulation with ${emotionalCount} emotional triggers.`;
        return `Significant manipulation with ${emotionalCount} emotional manipulations detected.`;
    },

    generateManipulationMeaning(score, riskLevel) {
        if (riskLevel === 'Low') return "Article presents information fairly.";
        if (riskLevel === 'Medium') return "Some persuasive techniques used.";
        return "High manipulation suggests agenda beyond information.";
    },

    generateContentFindings(score, readability) {
        const readText = readability !== 'Unknown' ? ` with ${readability} readability` : '';
        if (score >= 80) return `Excellent content quality${readText}.`;
        if (score >= 60) return `Good content quality${readText}.`;
        return `Poor content quality${readText}.`;
    },

    generateContentMeaning(level, score) {
        if (level === 'Excellent' || level === 'Good') return "Article meets professional standards.";
        if (level === 'Fair') return "Quality issues may affect understanding.";
        return "Poor quality undermines credibility.";
    },

    formatDomainAge(days) {
        if (!days) return 'Unknown';
        const years = Math.floor(days / 365);
        if (years >= 1) return `${years} year${years > 1 ? 's' : ''}`;
        return `${days} days`;
    },

    getVerificationLevel(score) {
        if (score >= 90) return 'Excellent';
        if (score >= 75) return 'High';
        if (score >= 60) return 'Good';
        if (score >= 40) return 'Moderate';
        return 'Low';
    },

    getTransparencyLevel(score, sources, quotes) {
        if (score >= 80 || (sources >= 10 && quotes >= 5)) return 'Very High';
        if (score >= 60 || (sources >= 5 && quotes >= 3)) return 'High';
        if (score >= 40 || (sources >= 3 && quotes >= 2)) return 'Moderate';
        return 'Low';
    },

    getManipulationRiskLevel(score) {
        if (score >= 70) return 'High';
        if (score >= 40) return 'Medium';
        return 'Low';
    },

    getQualityLevel(score) {
        if (score >= 80) return 'Excellent';
        if (score >= 60) return 'Good';
        if (score >= 40) return 'Fair';
        return 'Poor';
    },

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
    },

    displayClaimsList(data) {
        const section = document.getElementById('claimsCheckedSection');
        const list = document.getElementById('verifiedClaimsList');
        
        if (!section || !list) return;
        
        const claims = data.claims || data.verified_claims || [];
        
        if (claims.length > 0) {
            section.style.display = 'block';
            list.innerHTML = '';
            
            claims.forEach(claim => {
                const claimEl = document.createElement('div');
                claimEl.className = 'claim-item';
                
                const status = claim.verified ? 'verified' : 'unverified';
                const icon = status === 'verified' ? 'check-circle' : 'question-circle';
                const color = status === 'verified' ? 'green' : 'orange';
                
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
};

console.log('Enhanced service templates with source rankings loaded successfully');
