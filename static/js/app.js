/**
 * TruthLens News Analyzer - Complete Enhanced Version with Source Rankings
 * All 7 issues fixed with AI-powered analysis display + Source Rankings Feature
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

        // Source Rankings Data
        this.sourceRankingsData = {
            'reuters.com': { score: 95, rank: 1, trend: 'stable', category: 'highly-trusted' },
            'ap.org': { score: 94, rank: 2, trend: 'up', category: 'highly-trusted' },
            'bbc.com': { score: 92, rank: 3, trend: 'stable', category: 'highly-trusted' },
            'npr.org': { score: 90, rank: 4, trend: 'stable', category: 'highly-trusted' },
            'propublica.org': { score: 88, rank: 5, trend: 'up', category: 'highly-trusted' },
            'wsj.com': { score: 85, rank: 6, trend: 'stable', category: 'trusted' },
            'nytimes.com': { score: 84, rank: 7, trend: 'down', category: 'trusted' },
            'ft.com': { score: 83, rank: 8, trend: 'stable', category: 'trusted' },
            'economist.com': { score: 82, rank: 9, trend: 'stable', category: 'trusted' },
            'washingtonpost.com': { score: 80, rank: 10, trend: 'down', category: 'trusted' },
            'cnn.com': { score: 72, rank: 11, trend: 'stable', category: 'moderate' },
            'foxnews.com': { score: 70, rank: 12, trend: 'stable', category: 'moderate' },
            'msnbc.com': { score: 68, rank: 13, trend: 'down', category: 'moderate' },
            'politico.com': { score: 75, rank: 14, trend: 'up', category: 'trusted' },
            'axios.com': { score: 76, rank: 15, trend: 'up', category: 'trusted' }
        };

        // Source trend history (for future implementation)
        this.sourceTrendHistory = {};
        
        this.init();
        this.createServiceCards();
        this.initializeSourceRankings();
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

    initializeSourceRankings() {
        // Create the source rankings section if it doesn't exist
        const existingRankings = document.getElementById('sourceRankings');
        if (!existingRankings) {
            this.createSourceRankingsSection();
        }
    }

    createSourceRankingsSection() {
        // Find the best place to insert the rankings section
        const resultsSection = document.getElementById('resultsSection');
        if (!resultsSection) return;

        // Create the rankings HTML structure
        const rankingsHTML = `
            <div id="sourceRankings" class="source-rankings-container" style="display: none;">
                <div class="rankings-header">
                    <h3><i class="fas fa-trophy"></i> News Source Credibility Rankings</h3>
                    <p class="rankings-subtitle">How this source compares to others we've analyzed</p>
                </div>
                <div class="rankings-chart" id="rankingsChart">
                    <!-- Rankings will be inserted here -->
                </div>
                <div class="rankings-legend">
                    <div class="legend-item">
                        <span class="legend-color highly-trusted"></span>
                        <span class="legend-label">Highly Trusted (85-100)</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-color trusted"></span>
                        <span class="legend-label">Trusted (70-84)</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-color moderate"></span>
                        <span class="legend-label">Moderate (50-69)</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-color low"></span>
                        <span class="legend-label">Low Trust (Below 50)</span>
                    </div>
                </div>
            </div>
        `;

        // Insert after the analysis overview section
        const overviewSection = resultsSection.querySelector('#analysisOverview');
        if (overviewSection) {
            overviewSection.insertAdjacentHTML('afterend', rankingsHTML);
        }
    }

    displaySourceRankings(currentSource = null, currentScore = null) {
        const rankingsContainer = document.getElementById('sourceRankings');
        const rankingsChart = document.getElementById('rankingsChart');
        
        if (!rankingsContainer || !rankingsChart) {
            this.createSourceRankingsSection();
            return this.displaySourceRankings(currentSource, currentScore);
        }

        // Show the rankings section
        rankingsContainer.style.display = 'block';
        
        // Clear existing content
        rankingsChart.innerHTML = '';

        // Prepare data for display
        let rankingsToDisplay = Object.entries(this.sourceRankingsData)
            .sort((a, b) => b[1].score - a[1].score)
            .slice(0, 10); // Show top 10

        // Add current source if not in top 10
        if (currentSource) {
            const domain = this.extractDomain(currentSource);
            if (!this.sourceRankingsData[domain] && currentScore !== null) {
                // Add the current source to the display with animation
                const estimatedRank = this.calculateRank(currentScore);
                rankingsToDisplay.push([
                    domain,
                    {
                        score: currentScore,
                        rank: estimatedRank,
                        trend: 'new',
                        category: this.getScoreCategory(currentScore),
                        isCurrent: true
                    }
                ]);
                // Re-sort
                rankingsToDisplay.sort((a, b) => b[1].score - a[1].score);
            } else if (this.sourceRankingsData[domain]) {
                // Mark existing source as current
                rankingsToDisplay.forEach(([key, data]) => {
                    if (key === domain) {
                        data.isCurrent = true;
                    }
                });
            }
        }

        // Create ranking items
        rankingsToDisplay.forEach(([domain, data], index) => {
            const rankItem = this.createRankingItem(domain, data, index);
            rankingsChart.appendChild(rankItem);
        });

        // Add animation
        setTimeout(() => {
            rankingsChart.querySelectorAll('.ranking-item').forEach((item, index) => {
                setTimeout(() => {
                    item.classList.add('animate-in');
                }, index * 50);
            });
        }, 100);
    }

    createRankingItem(domain, data, index) {
        const item = document.createElement('div');
        item.className = `ranking-item ${data.category} ${data.isCurrent ? 'current-source' : ''}`;
        
        const trendIcon = this.getTrendIcon(data.trend);
        const rankChange = data.trend === 'up' ? '↑' : data.trend === 'down' ? '↓' : '−';
        
        item.innerHTML = `
            <div class="ranking-position">#${data.rank || index + 1}</div>
            <div class="ranking-source">
                <div class="source-name">${this.formatDomainName(domain)}</div>
                ${data.isCurrent ? '<span class="current-badge">Current Article</span>' : ''}
            </div>
            <div class="ranking-score-container">
                <div class="ranking-score-bar" style="width: ${data.score}%">
                    <span class="score-value">${data.score}/100</span>
                </div>
            </div>
            <div class="ranking-trend ${data.trend}">
                ${trendIcon}
            </div>
        `;

        if (data.isCurrent) {
            item.classList.add('highlight');
        }

        // Add click handler for more details
        item.addEventListener('click', () => {
            this.showSourceDetails(domain, data);
        });

        return item;
    }

    updateSourceRankings(analysisResults) {
        // Show the rankings section
        const rankingsContainer = document.getElementById('sourceRankings');
        if (rankingsContainer) {
            rankingsContainer.style.display = 'block';
        }
        
        // Extract source and score from analysis results
        const currentSource = analysisResults.source || null;
        const currentScore = analysisResults.trust_score || 
                           analysisResults.detailed_analysis?.source_credibility?.score || 
                           0;
        
        // Display rankings with current source highlighted
        this.displaySourceRankings(currentSource, currentScore);

        // Update historical data if we're tracking trends
        if (currentSource) {
            this.updateSourceTrend(currentSource, currentScore);
        }
    }

    updateSourceTrend(source, score) {
        const domain = this.extractDomain(source);
        
        if (!this.sourceTrendHistory[domain]) {
            this.sourceTrendHistory[domain] = [];
        }
        
        this.sourceTrendHistory[domain].push({
            score: score,
            timestamp: new Date().toISOString(),
            articleCount: this.sourceTrendHistory[domain].length + 1
        });

        // Calculate trend based on last 5 analyses
        if (this.sourceTrendHistory[domain].length >= 2) {
            const recent = this.sourceTrendHistory[domain].slice(-5);
            const avgRecent = recent.reduce((sum, item) => sum + item.score, 0) / recent.length;
            const firstScore = recent[0].score;
            
            if (avgRecent > firstScore + 2) {
                this.sourceRankingsData[domain] = {
                    ...this.sourceRankingsData[domain],
                    trend: 'up'
                };
            } else if (avgRecent < firstScore - 2) {
                this.sourceRankingsData[domain] = {
                    ...this.sourceRankingsData[domain],
                    trend: 'down'
                };
            }
        }
    }

    showSourceDetails(domain, data) {
        // Create a modal or tooltip with detailed information
        const detailsHTML = `
            <div class="source-details-modal">
                <h4>${this.formatDomainName(domain)}</h4>
                <p>Credibility Score: ${data.score}/100</p>
                <p>Ranking: #${data.rank}</p>
                <p>Category: ${data.category.replace('-', ' ').toUpperCase()}</p>
                <p>Trend: ${data.trend.toUpperCase()}</p>
                ${this.sourceTrendHistory[domain] ? 
                    `<p>Articles Analyzed: ${this.sourceTrendHistory[domain].length}</p>` : ''}
            </div>
        `;
        
        // You can implement a proper modal here
        console.log('Source details:', domain, data);
    }

    // Utility functions for source rankings
    extractDomain(url) {
        try {
            const urlObj = new URL(url.startsWith('http') ? url : 'https://' + url);
            return urlObj.hostname.replace('www.', '');
        } catch {
            return url.toLowerCase().replace('www.', '');
        }
    }

    formatDomainName(domain) {
        const nameMap = {
            'reuters.com': 'Reuters',
            'ap.org': 'Associated Press',
            'bbc.com': 'BBC News',
            'npr.org': 'NPR',
            'propublica.org': 'ProPublica',
            'wsj.com': 'Wall Street Journal',
            'nytimes.com': 'New York Times',
            'ft.com': 'Financial Times',
            'economist.com': 'The Economist',
            'washingtonpost.com': 'Washington Post',
            'cnn.com': 'CNN',
            'foxnews.com': 'Fox News',
            'msnbc.com': 'MSNBC',
            'politico.com': 'Politico',
            'axios.com': 'Axios'
        };
        return nameMap[domain] || domain.replace('.com', '').replace('.org', '');
    }

    getScoreCategory(score) {
        if (score >= 85) return 'highly-trusted';
        if (score >= 70) return 'trusted';
        if (score >= 50) return 'moderate';
        return 'low';
    }

    calculateRank(score) {
        let rank = 1;
        for (const [domain, data] of Object.entries(this.sourceRankingsData)) {
            if (data.score > score) rank++;
        }
        return rank;
    }

    getTrendIcon(trend) {
        const icons = {
            'up': '<i class="fas fa-arrow-up"></i>',
            'down': '<i class="fas fa-arrow-down"></i>',
            'stable': '<i class="fas fa-minus"></i>',
            'new': '<i class="fas fa-star"></i>'
        };
        return icons[trend] || icons['stable'];
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
        
        // Hide source rankings
        const rankingsContainer = document.getElementById('sourceRankings');
        if (rankingsContainer) {
            rankingsContainer.style.display = 'none';
        }
        
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
                // Add source rankings update
                this.updateSourceRankings(data);
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
