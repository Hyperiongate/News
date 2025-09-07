/**
 * FILE: static/js/app.js
 * FIXED VERSION - Last Updated: 2025-01-07
 * 
 * FIXES IMPLEMENTED:
 * 1. Empty Key Findings - Now generates meaningful findings from service data
 * 2. Missing Bias Visualization - Bias meter fully functional with proper positioning
 * 3. Fact Checking Logic Error - Correctly calculates 3/3 claims as 100%
 * 4. Missing Claim Details - Displays actual claims that were fact-checked
 * 5. Transparency Score Mismatch - 13 sources + 7 quotes = HIGH score
 * 6. OpenAI Enhancement Display - Shows AI-generated summaries and insights
 * 7. Author Information - Complete with LinkedIn, Wikipedia, bio, expertise
 * 
 * NOTES FOR FUTURE UPDATES:
 * - Service weights match backend: Source 25%, Bias 20%, Author 15%, Facts 15%, etc.
 * - Findings are extracted from multiple possible data formats
 * - All calculations fixed to match expected behavior
 * - Source rankings integrated and functional
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
        
        this.services = [
            { id: 'sourceCredibility', name: 'Source Credibility Analysis', icon: 'fa-shield-alt' },
            { id: 'biasDetector', name: 'Bias Detection Analysis', icon: 'fa-balance-scale' },
            { id: 'factChecker', name: 'Fact Checking Analysis', icon: 'fa-check-double' },
            { id: 'transparencyAnalyzer', name: 'Transparency Analysis', icon: 'fa-eye' },
            { id: 'manipulationDetector', name: 'Manipulation Detection', icon: 'fa-exclamation-triangle' },
            { id: 'contentAnalyzer', name: 'Content Analysis', icon: 'fa-file-alt' },
            { id: 'author', name: 'Author Analysis', icon: 'fa-user-shield' }
        ];

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

        this.sourceTrendHistory = {};
        this.init();
        this.createServiceCards();
        this.initializeSourceRankings();
    }

    init() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.resetBtn.addEventListener('click', this.handleReset.bind(this));
        this.urlInput.addEventListener('input', () => {
            if (this.urlInput.value) this.textInput.value = '';
        });
        this.textInput.addEventListener('input', () => {
            if (this.textInput.value) this.urlInput.value = '';
        });
    }

    initializeSourceRankings() {
        const existingRankings = document.getElementById('sourceRankings');
        if (!existingRankings) this.createSourceRankingsSection();
    }

    createSourceRankingsSection() {
        const resultsSection = document.getElementById('resultsSection');
        if (!resultsSection) return;

        const rankingsHTML = `
            <div id="sourceRankings" class="source-rankings-container" style="display: none;">
                <div class="rankings-header">
                    <h3><i class="fas fa-trophy"></i> News Source Credibility Rankings</h3>
                    <p class="rankings-subtitle">How this source compares to others we've analyzed</p>
                </div>
                <div class="rankings-chart" id="rankingsChart"></div>
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

        rankingsContainer.style.display = 'block';
        rankingsChart.innerHTML = '';

        let rankingsToDisplay = Object.entries(this.sourceRankingsData)
            .sort((a, b) => b[1].score - a[1].score)
            .slice(0, 10);

        if (currentSource) {
            const domain = this.extractDomain(currentSource);
            if (!this.sourceRankingsData[domain] && currentScore !== null) {
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
                rankingsToDisplay.sort((a, b) => b[1].score - a[1].score);
            } else if (this.sourceRankingsData[domain]) {
                rankingsToDisplay.forEach(([key, data]) => {
                    if (key === domain) data.isCurrent = true;
                });
            }
        }

        rankingsToDisplay.forEach(([domain, data], index) => {
            const rankItem = this.createRankingItem(domain, data, index);
            rankingsChart.appendChild(rankItem);
        });

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

        if (data.isCurrent) item.classList.add('highlight');
        item.addEventListener('click', () => this.showSourceDetails(domain, data));
        return item;
    }

    updateSourceRankings(analysisResults) {
        const rankingsContainer = document.getElementById('sourceRankings');
        if (rankingsContainer) rankingsContainer.style.display = 'block';
        
        const currentSource = analysisResults.source || null;
        const currentScore = analysisResults.trust_score || 
                           analysisResults.detailed_analysis?.source_credibility?.score || 0;
        
        this.displaySourceRankings(currentSource, currentScore);
        if (currentSource) this.updateSourceTrend(currentSource, currentScore);
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

        if (this.sourceTrendHistory[domain].length >= 2) {
            const recent = this.sourceTrendHistory[domain].slice(-5);
            const avgRecent = recent.reduce((sum, item) => sum + item.score, 0) / recent.length;
            const firstScore = recent[0].score;
            
            if (avgRecent > firstScore + 2) {
                this.sourceRankingsData[domain] = {...this.sourceRankingsData[domain], trend: 'up'};
            } else if (avgRecent < firstScore - 2) {
                this.sourceRankingsData[domain] = {...this.sourceRankingsData[domain], trend: 'down'};
            }
        }
    }

    showSourceDetails(domain, data) {
        console.log('Source details:', domain, data);
    }

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
                <div class="findings-list" id="sourceCredibilityFindings"></div>
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
                <div class="findings-list" id="transparencyAnalyzerFindings"></div>
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
                <div class="findings-list" id="manipulationDetectorFindings"></div>
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
    }

    getAuthorAnalysisTemplate() {
        return `
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
    }

    handleReset() {
        this.urlInput.value = '';
        this.textInput.value = '';
        this.resultsSection.classList.remove('show');
        this.progressContainer.classList.remove('active');
        this.resetProgress();
        
        const dropdowns = document.querySelectorAll('.service-dropdown');
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove('expanded');
        });
        
        const rankingsContainer = document.getElementById('sourceRankings');
        if (rankingsContainer) rankingsContainer.style.display = 'none';
        
        const debugInfo = document.getElementById('debugInfo');
        if (debugInfo) debugInfo.style.display = 'none';
        
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

        if (url) {
            try {
                new URL(url);
            } catch (e) {
                this.showError('Please enter a valid URL starting with http:// or https://');
                return;
            }
        }

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
        const steps = this.progressSteps?.querySelectorAll('.progress-step');
        if (steps) {
            steps.forEach(step => {
                step.classList.remove('active', 'completed');
            });
        }
    }

    updateProgressBar(progress) {
        if (this.progressBar) this.progressBar.style.width = progress + '%';
        if (this.progressPercentage) this.progressPercentage.textContent = Math.round(progress) + '%';
    }

    setActiveStep(stepIndex) {
        const steps = this.progressSteps?.querySelectorAll('.progress-step');
        if (steps) {
            steps.forEach((step, index) => {
                if (index === stepIndex) {
                    step.classList.add('active');
                } else {
                    step.classList.remove('active');
                }
            });
        }
    }

    setStepCompleted(stepIndex) {
        const step = this.progressSteps?.querySelector(`[data-step="${stepIndex}"]`);
        if (step) {
            step.classList.remove('active');
            step.classList.add('completed');
            const icon = step.querySelector('.step-icon');
            if (icon) icon.innerHTML = '<i class="fas fa-check"></i>';
        }
    }

    displayResults(data) {
        this.progressContainer.classList.remove('active');
        this.showDebugInfo(data);
        
        let trustScore = data.trust_score || 0;
        let articleSummary = data.article_summary || 'Analysis completed';
        let source = data.source || 'Unknown Source';
        let author = data.author || 'Staff Writer';
        
        // FIX 1: Generate meaningful findings summary from actual data
        let findingsSummary = this.generateFindingsSummary(data);
        
        this.updateTrustScore(trustScore);
        
        const overviewEl = document.getElementById('analysisOverview');
        if (overviewEl) {
            overviewEl.classList.remove('trust-high', 'trust-medium', 'trust-low');
            if (trustScore >= 70) {
                overviewEl.classList.add('trust-high');
            } else if (trustScore >= 40) {
                overviewEl.classList.add('trust-medium');
            } else {
                overviewEl.classList.add('trust-low');
            }
        }
        
        document.getElementById('articleSummary').textContent = 
            articleSummary.length > 100 ? articleSummary.substring(0, 100) + '...' : articleSummary;
        document.getElementById('articleSource').textContent = source;
        document.getElementById('articleAuthor').textContent = author;
        document.getElementById('findingsSummary').textContent = findingsSummary;
        
        this.displayAllServiceAnalyses(data);
        this.showResults();
    }

    // FIX 1: Generate meaningful findings summary
    generateFindingsSummary(data) {
        const detailed = data.detailed_analysis || {};
        const findings = [];
        
        // Extract key findings from each service
        if (detailed.source_credibility?.score) {
            const score = detailed.source_credibility.score;
            if (score >= 80) findings.push('Highly credible source identified');
            else if (score >= 60) findings.push('Generally credible source');
            else findings.push('Source credibility concerns detected');
        }
        
        if (detailed.bias_detector?.bias_score !== undefined) {
            const bias = detailed.bias_detector.bias_score;
            if (bias < 30) findings.push('Minimal bias detected');
            else if (bias < 60) findings.push('Moderate bias present');
            else findings.push('Significant bias detected');
        }
        
        if (detailed.fact_checker) {
            const verified = detailed.fact_checker.claims_verified || 0;
            const total = detailed.fact_checker.claims_found || 0;
            if (total > 0) {
                findings.push(`${verified} of ${total} claims verified`);
            }
        }
        
        if (detailed.transparency_analyzer) {
            const sources = detailed.transparency_analyzer.source_count || 0;
            const quotes = detailed.transparency_analyzer.quote_count || 0;
            if (sources > 0 || quotes > 0) {
                findings.push(`${sources} sources cited, ${quotes} quotes included`);
            }
        }
        
        if (findings.length === 0) {
            return data.findings_summary || 'Comprehensive analysis completed. Review individual service results for detailed insights.';
        }
        
        return findings.join('. ') + '.';
    }

    updateTrustScore(score) {
        const scoreElement = document.getElementById('trustScore');
        const labelElement = document.getElementById('trustLabel');
        
        if (scoreElement) scoreElement.textContent = Math.round(score);
        
        if (labelElement) {
            if (score >= 80) {
                labelElement.textContent = 'Highly Trustworthy';
                if (scoreElement) scoreElement.className = 'trust-score-number trust-high';
            } else if (score >= 60) {
                labelElement.textContent = 'Generally Trustworthy';
                if (scoreElement) scoreElement.className = 'trust-score-number trust-medium';
            } else if (score >= 40) {
                labelElement.textContent = 'Moderate Trust';
                if (scoreElement) scoreElement.className = 'trust-score-number trust-medium';
            } else {
                labelElement.textContent = 'Low Trustworthiness';
                if (scoreElement) scoreElement.className = 'trust-score-number trust-low';
            }
        }
    }

    cleanAuthorName(rawAuthor) {
        // Handle various malformed author formats from backend
        if (!rawAuthor || rawAuthor === 'Unknown') return rawAuthor;
        
        let cleaned = rawAuthor;
        
        // Remove "By" or "ByXXX" prefix (handle cases with no space after By)
        cleaned = cleaned.replace(/^By\s*/i, '');
        
        // Handle "ByRick Pearson|rpearson@chicagotribune.com| Chicago Tribune" format
        if (cleaned.includes('|')) {
            // Take only the first part before the pipe
            cleaned = cleaned.split('|')[0].trim();
        }
        
        // Handle "Mary Clare Jalonick, Associated PressMary Clare Jalonick, Associated Press" duplication
        if (cleaned.length > 40) {
            // Check for exact duplication
            const halfLength = Math.floor(cleaned.length / 2);
            const firstHalf = cleaned.substring(0, halfLength);
            const secondHalf = cleaned.substring(halfLength);
            
            if (firstHalf === secondHalf) {
                cleaned = firstHalf;
            } else {
                // Check for partial duplication (name appears twice)
                const nameParts = cleaned.split(',')[0];
                if (nameParts && cleaned.lastIndexOf(nameParts) > nameParts.length) {
                    // Name appears twice, take only first occurrence
                    const commaIndex = cleaned.indexOf(',');
                    if (commaIndex > 0 && commaIndex < cleaned.length / 2) {
                        cleaned = cleaned.substring(0, cleaned.indexOf(nameParts, nameParts.length));
                    }
                }
            }
        }
        
        // Remove "UPDATED" or timestamp data that might be concatenated
        cleaned = cleaned.replace(/UPDATED:.*$/i, '').trim();
        cleaned = cleaned.replace(/\d{4} at \d{1,2}:\d{2}.*$/i, '').trim();
        
        // Remove email addresses
        cleaned = cleaned.replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '').trim();
        
        // Clean up organization names that might be concatenated
        // If we have something like "John Smith, Reuters" or "John Smith, Associated Press"
        if (cleaned.includes(',')) {
            const parts = cleaned.split(',');
            if (parts.length === 2) {
                const possibleOrg = parts[1].trim();
                // Keep the organization if it's reasonable length
                if (possibleOrg.length < 30 && !possibleOrg.includes('Press') && !possibleOrg.includes('Tribune')) {
                    cleaned = parts[0].trim(); // Just the name
                }
            }
        }
        
        // Final cleanup - remove any remaining special characters at the edges
        cleaned = cleaned.replace(/^[|\s-]+|[|\s-]+$/g, '').trim();
        
        // Validate the result
        if (cleaned.length < 3 || cleaned.length > 100) {
            return 'Unknown';
        }
        
        return cleaned;
    }

    displayAllServiceAnalyses(data) {
        console.log('=== FULL ANALYSIS DATA DIAGNOSTIC ===');
        console.log('Complete response data:', data);
        console.log('Response data keys:', Object.keys(data));
        
        const detailed_analysis = data.detailed_analysis || {};
        console.log('Detailed analysis object:', detailed_analysis);
        console.log('Detailed analysis keys:', Object.keys(detailed_analysis));
        
        // Log each service's data
        console.log('Service data breakdown:');
        Object.entries(detailed_analysis).forEach(([service, serviceData]) => {
            console.log(`  ${service}:`, serviceData);
        });
        
        // Specific author data check
        console.log('Author analyzer data:', detailed_analysis.author_analyzer);
        console.log('Top-level author field:', data.author);
        
        this.displaySourceCredibility(detailed_analysis.source_credibility || {});
        this.displayBiasDetection(detailed_analysis.bias_detector || {});
        this.displayFactChecking(detailed_analysis.fact_checker || {});
        this.displayTransparencyAnalysis(detailed_analysis.transparency_analyzer || {});
        this.displayManipulationDetection(detailed_analysis.manipulation_detector || {});
        this.displayContentAnalysis(detailed_analysis.content_analyzer || {}, detailed_analysis.openai_enhancer || {});
        this.displayAuthorAnalysis(detailed_analysis.author_analyzer || {}, data.author);
    }

    displaySourceCredibility(data) {
        const score = data.score || 0;
        const rating = data.credibility || 'Unknown';
        const biasLevel = data.bias || 'Unknown';
        const domainAge = data.domain_age_days ? this.formatDomainAge(data.domain_age_days) : 'Unknown';
        
        document.getElementById('sourceCredibilityScore').textContent = `${score}/100`;
        document.getElementById('sourceCredibilityRating').textContent = rating;
        document.getElementById('sourceBiasLevel').textContent = biasLevel;
        document.getElementById('sourceDomainAge').textContent = domainAge;
        
        // FIX 1: Generate real findings
        const findings = this.generateRealFindings('credibility', data);
        const findingsEl = document.getElementById('sourceCredibilityFindings');
        if (findingsEl) findingsEl.innerHTML = findings;
        
        const interpretation = this.generateInterpretation('credibility', score);
        const interpEl = document.getElementById('sourceCredibilityInterpretation');
        if (interpEl) interpEl.textContent = interpretation;
    }

    displayBiasDetection(data) {
        const biasScore = data.bias_score || data.score || 0;
        const politicalLean = data.dimensions?.political?.label || data.political_lean || 'Neutral';
        const dominantBias = data.dominant_bias || 'None';
        const objectivityScore = data.objectivity_score !== undefined ? data.objectivity_score : (100 - biasScore);
        
        document.getElementById('biasScore').textContent = `${biasScore}/100`;
        document.getElementById('politicalLean').textContent = politicalLean;
        document.getElementById('dominantBias').textContent = dominantBias;
        document.getElementById('objectivityScore').textContent = `${objectivityScore}%`;
        
        // FIX 2: Update bias meter properly
        this.updateBiasMeter(politicalLean, biasScore);
        
        const findings = this.generateRealFindings('bias', data);
        const findingsEl = document.getElementById('biasDetectorFindings');
        if (findingsEl) findingsEl.innerHTML = findings;
        
        const interpretation = this.generateInterpretation('bias', biasScore, objectivityScore);
        const interpEl = document.getElementById('biasDetectorInterpretation');
        if (interpEl) interpEl.textContent = interpretation;
    }

    displayFactChecking(data) {
        const claimsAnalyzed = data.claims_found || 0;
        const claimsVerified = data.claims_verified || 0;
        let verificationScore = 0;
        
        // FIX 3: Correct fact checking calculation
        if (claimsAnalyzed > 0) {
            verificationScore = Math.round((claimsVerified / claimsAnalyzed) * 100);
        } else {
            verificationScore = data.score || 0;
        }
        
        const verificationLevel = this.getVerificationLevel(verificationScore);
        
        document.getElementById('verificationScore').textContent = `${verificationScore}/100`;
        document.getElementById('claimsAnalyzed').textContent = claimsAnalyzed;
        document.getElementById('claimsVerified').textContent = claimsVerified;
        document.getElementById('verificationLevel').textContent = verificationLevel;
        
        // FIX 4: Display actual claims
        this.displayClaimsList(data);
        
        const findings = this.generateRealFindings('fact', data);
        const findingsEl = document.getElementById('factCheckerFindings');
        if (findingsEl) findingsEl.innerHTML = findings;
        
        const interpretation = this.generateInterpretation('fact', verificationScore);
        const interpEl = document.getElementById('factCheckerInterpretation');
        if (interpEl) interpEl.textContent = interpretation;
    }

    displayTransparencyAnalysis(data) {
        const sourcesCited = data.source_count || 0;
        const quotesUsed = data.quote_count || 0;
        
        // FIX 5: Correct transparency calculation
        let transparencyScore;
        if (sourcesCited > 0 || quotesUsed > 0) {
            const sourceScore = Math.min(sourcesCited * 8, 50);
            const quoteScore = Math.min(quotesUsed * 10, 50);
            transparencyScore = Math.min(sourceScore + quoteScore, 100);
        } else {
            transparencyScore = data.score || 0;
        }
        
        const disclosureLevel = this.getTransparencyLevel(transparencyScore, sourcesCited, quotesUsed);
        
        document.getElementById('transparencyScore').textContent = `${transparencyScore}/100`;
        document.getElementById('sourcesCited').textContent = sourcesCited;
        document.getElementById('quotesUsed').textContent = quotesUsed;
        document.getElementById('disclosureLevel').textContent = disclosureLevel;
        
        const findings = this.generateRealFindings('transparency', data);
        const findingsEl = document.getElementById('transparencyAnalyzerFindings');
        if (findingsEl) findingsEl.innerHTML = findings;
        
        const interpretation = this.generateInterpretation('transparency', transparencyScore);
        const interpEl = document.getElementById('transparencyAnalyzerInterpretation');
        if (interpEl) interpEl.textContent = interpretation;
    }

    displayManipulationDetection(data) {
        const manipulationScore = data.score || 0;
        const riskLevel = this.getManipulationRiskLevel(manipulationScore);
        const techniques = data.manipulation_techniques || [];
        const emotionalCount = data.emotional_language_count || 0;
        
        document.getElementById('manipulationScore').textContent = `${manipulationScore}/100`;
        document.getElementById('manipulationRiskLevel').textContent = riskLevel;
        document.getElementById('manipulationTechniques').textContent = techniques.length;
        document.getElementById('emotionalLanguageCount').textContent = emotionalCount;
        
        const findings = this.generateRealFindings('manipulation', data);
        const findingsEl = document.getElementById('manipulationDetectorFindings');
        if (findingsEl) findingsEl.innerHTML = findings;
        
        const interpretation = this.generateInterpretation('manipulation', manipulationScore, riskLevel);
        const interpEl = document.getElementById('manipulationDetectorInterpretation');
        if (interpEl) interpEl.textContent = interpretation;
    }

    displayContentAnalysis(contentData, openaiData) {
        const qualityScore = contentData.score || 0;
        const qualityLevel = this.getQualityLevel(qualityScore);
        const readability = contentData.readability || 'Unknown';
        const structureScore = contentData.structure_score || 'Unknown';
        
        // FIX 6: Display OpenAI enhancements
        const aiInsights = openaiData?.summary || openaiData?.analysis || '';
        const keyPoints = openaiData?.key_points || [];
        
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
                        ${aiInsights ? `
                            <h5>AI-Generated Analysis</h5>
                            <p>${aiInsights}</p>
                        ` : ''}
                        ${keyPoints.length > 0 ? `
                            <h5>Key Insights</h5>
                            <ul>${keyPoints.map(point => `<li>${point}</li>`).join('')}</ul>
                        ` : ''}
                    </div>
                `;
            }
        }
        
        const findings = this.generateRealFindings('content', contentData);
        const findingsEl = document.getElementById('contentAnalyzerFindings');
        if (findingsEl) findingsEl.innerHTML = findings;
        
        const interpretation = this.generateInterpretation('content', qualityScore);
        const interpEl = document.getElementById('contentAnalyzerInterpretation');
        if (interpEl) interpEl.textContent = interpretation;
    }

    displayAuthorAnalysis(data, fallbackAuthor) {
        // FIX 7: Complete author information display
        // Handle cases where author name might be duplicated or concatenated
        let authorName = data.author_name || data.name || fallbackAuthor || 'Unknown';
        
        // Fix duplicated author names (e.g., "Mary Clare Jalonick, Associated PressMary Clare Jalonick, Associated Press")
        if (authorName.length > 50 && authorName.indexOf(authorName.substring(0, 20)) > 20) {
            // Check if the name appears to be duplicated
            const halfLength = Math.floor(authorName.length / 2);
            const firstHalf = authorName.substring(0, halfLength);
            const secondHalf = authorName.substring(halfLength);
            if (firstHalf === secondHalf || firstHalf.includes(secondHalf.split(',')[0])) {
                authorName = firstHalf;
            }
        }
        
        const authorScore = data.score || data.credibility_score || 0;
        const authorPosition = data.position || data.title || data.role || 'Writer';
        const authorBio = data.bio || data.biography || data.description || '';
        
        document.getElementById('authorName').textContent = authorName;
        document.getElementById('authorPosition').textContent = authorPosition;
        document.getElementById('authorCredibilityScore').textContent = authorScore > 0 ? `${authorScore}/100` : 'N/A';
        
        if (authorBio) {
            document.getElementById('authorBio').style.display = 'block';
            document.getElementById('authorBioText').textContent = authorBio;
        }
        
        // Display author profiles (LinkedIn, Wikipedia, etc.)
        const profiles = this.extractAuthorProfiles(data);
        this.displayAuthorProfiles(profiles);
        
        // Display expertise areas
        const expertise = data.expertise_areas || data.expertise || [];
        this.displayExpertise(expertise);
        
        // Display publication history
        const publications = data.recent_articles || data.publications || [];
        this.displayPublicationHistory(publications);
        
        // Display awards
        const awards = data.awards || [];
        this.displayAwards(awards);
        
        // Update stats
        document.getElementById('articleCount').textContent = publications.length || data.article_count || 0;
        document.getElementById('profilesCount').textContent = Object.keys(profiles).length || 0;
        document.getElementById('awardsCount').textContent = awards.length || 0;
    }

    // FIX 1 Helper: Generate real findings from data
    generateRealFindings(type, data) {
        let content = '<div class="service-analysis-section">';
        
        // What We Analyzed
        content += '<div class="analysis-block">';
        content += '<h4><i class="fas fa-search"></i> What We Analyzed</h4>';
        content += '<p>';
        
        switch(type) {
            case 'credibility':
                content += 'Source reputation, domain history, industry recognition, and historical accuracy.';
                break;
            case 'bias':
                content += 'Political orientation, language patterns, balanced reporting, and objectivity markers.';
                break;
            case 'fact':
                content += 'Verifiable claims, factual statements, statistical data, and cross-reference accuracy.';
                break;
            case 'transparency':
                content += 'Source citations, direct quotes, author disclosure, and reference transparency.';
                break;
            case 'manipulation':
                content += 'Emotional language, persuasion techniques, logical fallacies, and misleading content.';
                break;
            case 'content':
                content += 'Writing quality, structure, readability, depth of coverage, and journalistic standards.';
                break;
        }
        
        content += '</p></div>';
        
        // What We Found
        content += '<div class="analysis-block">';
        content += '<h4><i class="fas fa-clipboard-check"></i> What We Found</h4>';
        content += '<p>';
        
        // Extract actual findings from data
        const findings = this.extractServiceFindings(type, data);
        content += findings;
        
        content += '</p></div>';
        
        // What This Means
        content += '<div class="analysis-block">';
        content += '<h4><i class="fas fa-lightbulb"></i> What This Means</h4>';
        content += '<p>';
        content += this.getServiceMeaning(type, data);
        content += '</p></div>';
        
        content += '</div>';
        return content;
    }

    extractServiceFindings(type, data) {
        const findings = [];
        
        switch(type) {
            case 'credibility':
                if (data.score) findings.push(`Credibility score: ${data.score}/100`);
                if (data.credibility) findings.push(`Rating: ${data.credibility}`);
                if (data.bias) findings.push(`Bias level: ${data.bias}`);
                if (data.domain_age_days) findings.push(`Domain age: ${this.formatDomainAge(data.domain_age_days)}`);
                break;
                
            case 'bias':
                if (data.bias_score !== undefined) findings.push(`Bias intensity: ${data.bias_score}/100`);
                if (data.political_lean) findings.push(`Political lean: ${data.political_lean}`);
                if (data.dominant_bias) findings.push(`Primary bias: ${data.dominant_bias}`);
                if (data.objectivity_score !== undefined) findings.push(`Objectivity: ${data.objectivity_score}%`);
                break;
                
            case 'fact':
                if (data.claims_found) findings.push(`${data.claims_found} claims analyzed`);
                if (data.claims_verified) findings.push(`${data.claims_verified} claims verified`);
                if (data.accuracy_rate) findings.push(`Accuracy rate: ${data.accuracy_rate}%`);
                break;
                
            case 'transparency':
                if (data.source_count) findings.push(`${data.source_count} sources cited`);
                if (data.quote_count) findings.push(`${data.quote_count} direct quotes`);
                if (data.author_disclosure) findings.push('Author disclosure present');
                break;
                
            case 'manipulation':
                if (data.manipulation_techniques?.length) {
                    findings.push(`${data.manipulation_techniques.length} manipulation techniques detected`);
                }
                if (data.emotional_language_count) {
                    findings.push(`${data.emotional_language_count} emotional terms used`);
                }
                break;
                
            case 'content':
                if (data.quality_score) findings.push(`Quality score: ${data.quality_score}/100`);
                if (data.readability) findings.push(`Readability: ${data.readability}`);
                if (data.structure_score) findings.push(`Structure: ${data.structure_score}`);
                break;
        }
        
        return findings.length > 0 ? findings.join(', ') : 'Analysis completed successfully';
    }

    getServiceMeaning(type, data) {
        switch(type) {
            case 'credibility':
                const credScore = data.score || 0;
                if (credScore >= 80) return 'This source has an excellent reputation and is highly reliable for news content.';
                if (credScore >= 60) return 'This source is generally credible with a good track record.';
                if (credScore >= 40) return 'This source has mixed credibility - verify important information.';
                return 'This source has credibility concerns - seek additional verification.';
                
            case 'bias':
                const biasScore = data.bias_score || 0;
                if (biasScore < 30) return 'Content shows minimal bias with balanced reporting.';
                if (biasScore < 50) return 'Some bias detected but within acceptable journalism standards.';
                if (biasScore < 70) return 'Significant bias present - consider alternative perspectives.';
                return 'Heavy bias detected - this appears to be opinion or advocacy content.';
                
            case 'fact':
                const verified = data.claims_verified || 0;
                const total = data.claims_found || 0;
                if (total === 0) return 'No specific factual claims found to verify.';
                const rate = (verified / total) * 100;
                if (rate >= 90) return 'Excellent factual accuracy with verified claims.';
                if (rate >= 70) return 'Good factual accuracy with most claims verified.';
                if (rate >= 50) return 'Mixed factual accuracy - some claims could not be verified.';
                return 'Low factual accuracy - many claims unverified or incorrect.';
                
            case 'transparency':
                const sources = data.source_count || 0;
                const quotes = data.quote_count || 0;
                if (sources >= 10 && quotes >= 5) return 'Excellent transparency with comprehensive sourcing.';
                if (sources >= 5 && quotes >= 3) return 'Good transparency with adequate sourcing.';
                if (sources >= 2 || quotes >= 1) return 'Limited transparency - more sources would strengthen credibility.';
                return 'Poor transparency - lacks proper sourcing and attribution.';
                
            case 'manipulation':
                const manipScore = data.score || 0;
                if (manipScore < 30) return 'Content appears straightforward with minimal manipulation.';
                if (manipScore < 50) return 'Some persuasive techniques used but within normal bounds.';
                if (manipScore < 70) return 'Notable manipulation techniques present - read critically.';
                return 'Heavy manipulation detected - approach with significant caution.';
                
            case 'content':
                const qualityScore = data.score || 0;
                if (qualityScore >= 80) return 'Excellent content quality meeting professional standards.';
                if (qualityScore >= 60) return 'Good content quality with minor issues.';
                if (qualityScore >= 40) return 'Fair content quality with room for improvement.';
                return 'Poor content quality - lacks professional standards.';
                
            default:
                return 'Analysis complete - see detailed metrics above.';
        }
    }

    generateInterpretation(type, score, additional) {
        switch(type) {
            case 'credibility':
                if (score >= 80) return 'This source demonstrates exceptional credibility with a strong track record of accurate reporting and professional journalism standards.';
                if (score >= 60) return 'Generally reliable source with good credibility, though some limitations may exist in coverage or occasional inaccuracies.';
                if (score >= 40) return 'Mixed credibility with both strengths and concerns. Cross-reference important information with other sources.';
                return 'Significant credibility concerns detected. Exercise caution and verify all claims through additional sources.';
            
            case 'bias':
                const objectivity = additional || (100 - score);
                if (score < 30) return `Excellent objectivity (${objectivity}% neutral). Content shows balanced reporting with minimal ideological influence.`;
                if (score < 50) return `Good objectivity (${objectivity}% neutral). Some bias present but maintains journalistic standards.`;
                if (score < 70) return `Moderate objectivity (${objectivity}% neutral). Clear perspective evident - seek alternative viewpoints for balance.`;
                return `Low objectivity (${objectivity}% neutral). Strong bias detected - this appears to be opinion or advocacy content.`;
            
            case 'fact':
                if (score >= 90) return 'Outstanding factual accuracy. Claims are well-supported with verifiable evidence.';
                if (score >= 70) return 'Good factual reliability with most claims verified. Minor issues may exist.';
                if (score >= 50) return 'Mixed factual accuracy. Several claims could not be verified or contain errors.';
                return 'Significant factual concerns. Many claims are unverified or demonstrably incorrect.';
            
            case 'transparency':
                if (score >= 80) return 'Exemplary transparency with comprehensive source attribution and clear methodology.';
                if (score >= 60) return 'Good transparency practices with adequate sourcing and disclosure.';
                if (score >= 40) return 'Limited transparency. Additional sourcing and attribution would improve credibility.';
                return 'Poor transparency. Lacks essential sourcing, making verification difficult.';
            
            case 'manipulation':
                if (score < 30) return 'Content appears genuine and straightforward with minimal persuasive tactics.';
                if (score < 50) return 'Some rhetorical techniques present but within acceptable bounds for persuasive writing.';
                if (score < 70) return 'Significant manipulation techniques detected. Read with critical awareness of persuasive intent.';
                return 'Heavy manipulation present. Content uses multiple techniques to influence reader opinion.';
            
            case 'content':
                if (score >= 80) return 'Professional-quality content with excellent structure, clarity, and depth of coverage.';
                if (score >= 60) return 'Well-written content with good organization, though some areas could be improved.';
                if (score >= 40) return 'Adequate content quality with noticeable issues in structure or clarity.';
                return 'Below-standard content quality. Lacks professional writing and organizational standards.';
            
            default:
                return 'Analysis completed successfully.';
        }
    }

    // Helper methods
    formatDomainAge(days) {
        if (!days) return 'Unknown';
        const years = Math.floor(days / 365);
        if (years >= 1) return `${years} year${years > 1 ? 's' : ''}`;
        return `${days} days`;
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
        return 'Low';
    }

    getManipulationRiskLevel(score) {
        if (score >= 70) return 'High';
        if (score >= 40) return 'Medium';
        return 'Low';
    }

    getQualityLevel(score) {
        if (score >= 80) return 'Excellent';
        if (score >= 60) return 'Good';
        if (score >= 40) return 'Fair';
        return 'Poor';
    }

    // FIX 2: Properly update bias meter
    updateBiasMeter(politicalLean, biasScore) {
        const indicator = document.getElementById('biasIndicator');
        if (!indicator) return;
        
        let position = 50; // Default center
        const leanMap = {
            'far left': 10,
            'left': 30,
            'center-left': 40,
            'center': 50,
            'center-right': 60,
            'right': 70,
            'far right': 90
        };
        
        // Check for political lean matches
        const leanLower = politicalLean.toLowerCase();
        for (const [key, value] of Object.entries(leanMap)) {
            if (leanLower.includes(key)) {
                position = value;
                break;
            }
        }
        
        // Apply position with animation
        indicator.style.left = `${position}%`;
        
        // Color based on bias intensity
        if (biasScore >= 70) {
            indicator.style.backgroundColor = '#ef4444'; // Red for high bias
        } else if (biasScore >= 50) {
            indicator.style.backgroundColor = '#f59e0b'; // Orange for medium
        } else if (biasScore >= 30) {
            indicator.style.backgroundColor = '#eab308'; // Yellow for low-medium
        } else {
            indicator.style.backgroundColor = '#10b981'; // Green for low bias
        }
    }

    // FIX 4: Display actual claims list
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
                
                const status = claim.verified !== false ? 'verified' : 'unverified';
                const icon = status === 'verified' ? 'check-circle' : 'times-circle';
                const color = status === 'verified' ? '#10b981' : '#ef4444';
                
                claimEl.innerHTML = `
                    <div class="claim-status ${status}">
                        <i class="fas fa-${icon}" style="color: ${color}"></i>
                    </div>
                    <div class="claim-text">
                        ${claim.text || claim.claim || 'Claim analyzed'}
                        ${claim.evidence ? `<div class="claim-evidence">${claim.evidence}</div>` : ''}
                    </div>
                `;
                
                list.appendChild(claimEl);
            });
        } else if (data.claims_found > 0) {
            // If we have counts but no actual claims, show summary
            section.style.display = 'block';
            list.innerHTML = `
                <div class="claim-item">
                    <div class="claim-status verified">
                        <i class="fas fa-info-circle" style="color: #3b82f6"></i>
                    </div>
                    <div class="claim-text">
                        ${data.claims_verified} out of ${data.claims_found} factual claims were successfully verified
                    </div>
                </div>
            `;
        } else {
            section.style.display = 'none';
        }
    }

    // FIX 7: Extract author profiles
    extractAuthorProfiles(data) {
        const profiles = {};
        
        // Check multiple possible field names
        if (data.linkedin_profile || data.linkedin) {
            profiles.linkedin = data.linkedin_profile || data.linkedin;
        }
        if (data.twitter_profile || data.twitter || data.x_profile) {
            profiles.twitter = data.twitter_profile || data.twitter || data.x_profile;
        }
        if (data.wikipedia_page || data.wikipedia) {
            profiles.wikipedia = data.wikipedia_page || data.wikipedia;
        }
        if (data.muckrack_profile || data.muckrack) {
            profiles.muckrack = data.muckrack_profile || data.muckrack;
        }
        if (data.website || data.personal_website) {
            profiles.website = data.website || data.personal_website;
        }
        
        return profiles;
    }

    displayAuthorProfiles(profiles) {
        const profilesSection = document.getElementById('authorProfiles');
        const profilesGrid = document.getElementById('profilesGrid');
        
        if (!profilesGrid) return;
        profilesGrid.innerHTML = '';
        
        if (Object.keys(profiles).length > 0) {
            if (profilesSection) profilesSection.style.display = 'block';
            
            Object.entries(profiles).forEach(([platform, url]) => {
                if (url) {
                    const link = document.createElement('a');
                    link.className = `profile-link ${platform}`;
                    link.href = url;
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                    
                    const iconMap = {
                        linkedin: 'fab fa-linkedin',
                        twitter: 'fab fa-twitter',
                        wikipedia: 'fab fa-wikipedia-w',
                        muckrack: 'fas fa-newspaper',
                        website: 'fas fa-globe'
                    };
                    
                    link.innerHTML = `<i class="${iconMap[platform] || 'fas fa-link'}"></i> ${platform.charAt(0).toUpperCase() + platform.slice(1)}`;
                    profilesGrid.appendChild(link);
                }
            });
        } else {
            if (profilesSection) profilesSection.style.display = 'none';
        }
    }

    displayExpertise(expertise) {
        const section = document.getElementById('expertiseSection');
        const tagsContainer = document.getElementById('expertiseTags');
        
        if (!section || !tagsContainer) return;
        
        if (expertise && expertise.length > 0) {
            section.style.display = 'block';
            tagsContainer.innerHTML = '';
            
            expertise.forEach(area => {
                const tag = document.createElement('span');
                tag.className = 'expertise-tag';
                tag.textContent = area;
                tagsContainer.appendChild(tag);
            });
        } else {
            section.style.display = 'none';
        }
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
                pubEl.innerHTML = `
                    <div class="pub-title">${pub.title || 'Untitled'}</div>
                    ${pub.source || pub.date ? `
                        <div class="pub-meta">
                            ${pub.source ? `<span class="pub-source">${pub.source}</span>` : ''}
                            ${pub.date ? `<span class="pub-date">${pub.date}</span>` : ''}
                        </div>
                    ` : ''}
                `;
                list.appendChild(pubEl);
            });
        } else {
            section.style.display = 'none';
        }
    }

    displayAwards(awards) {
        const section = document.getElementById('awardsSection');
        const list = document.getElementById('awardsList');
        
        if (!section || !list) return;
        
        if (awards && awards.length > 0) {
            section.style.display = 'block';
            list.innerHTML = '';
            
            awards.forEach(award => {
                const awardEl = document.createElement('div');
                awardEl.className = 'award-item';
                awardEl.innerHTML = `
                    <div class="award-icon">
                        <i class="fas fa-trophy"></i>
                    </div>
                    <div class="award-text">${award.name || award}</div>
                `;
                list.appendChild(awardEl);
            });
        } else {
            section.style.display = 'none';
        }
    }

    showDebugInfo(data) {
        const debugInfo = document.getElementById('debugInfo');
        const debugData = document.getElementById('debugData');
        
        if (debugInfo && debugData && 
            (window.location.hostname === 'localhost' || 
             window.location.hostname.includes('render'))) {
            
            debugData.textContent = JSON.stringify({
                success: data.success,
                trust_score: data.trust_score,
                source: data.source,
                author: data.author,
                detailed_analysis_keys: data.detailed_analysis ? Object.keys(data.detailed_analysis) : [],
                services_with_data: data.detailed_analysis ? 
                    Object.entries(data.detailed_analysis)
                        .filter(([key, val]) => val && Object.keys(val).length > 0)
                        .map(([key]) => key) : []
            }, null, 2);
            debugInfo.style.display = 'block';
        }
    }

    showResults() {
        if (this.resultsSection) {
            this.resultsSection.classList.add('show');
            this.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    setLoading(loading) {
        if (this.analyzeBtn) {
            this.analyzeBtn.disabled = loading;
            this.analyzeBtn.innerHTML = loading ? 
                '<div class="button-content"><i class="fas fa-spinner fa-spin"></i> Analyzing...</div>' :
                '<div class="button-content"><i class="fas fa-search"></i> Analyze Article</div>';
        }
        
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.classList[loading ? 'add' : 'remove']('active');
        }
    }

    showError(message) {
        if (this.progressContainer) {
            this.progressContainer.classList.remove('active');
        }
        
        const errorEl = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        
        if (errorEl && errorText) {
            errorText.textContent = message;
            errorEl.classList.add('active');
            setTimeout(() => errorEl.classList.remove('active'), 8000);
        }
        console.error('Analysis error:', message);
    }

    hideError() {
        const errorEl = document.getElementById('errorMessage');
        if (errorEl) errorEl.classList.remove('active');
    }
}

// Global function for toggling service dropdowns
window.toggleServiceDropdown = function(serviceName) {
    const dropdown = document.getElementById(serviceName + 'Dropdown');
    if (dropdown) dropdown.classList.toggle('expanded');
}

// Initialize application on DOM load
document.addEventListener('DOMContentLoaded', () => {
    const analyzer = new TruthLensAnalyzer();
    window.truthLensAnalyzer = analyzer;
    console.log('TruthLens Analyzer initialized - Version 2025-01-07');
});

// Export for use
window.TruthLensAnalyzer = TruthLensAnalyzer;
