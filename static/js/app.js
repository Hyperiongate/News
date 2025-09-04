/**
 * TruthLens News Analyzer - Complete Enhanced Version with Source Rankings
 * All functionality preserved - optimized for deployment
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
        let findingsSummary = data.findings_summary || 'Analysis completed successfully';
        
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

    displayAllServiceAnalyses(data) {
        console.log('=== Displaying All Service Analyses ===');
        const detailed_analysis = data.detailed_analysis || {};
        
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
        
        const findings = this.generateFindings('credibility', score, rating, biasLevel, data);
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
        
        this.updateBiasMeter(politicalLean, biasScore);
        
        const findings = this.generateFindings('bias', biasScore, politicalLean, dominantBias);
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
        
        this.displayClaimsList(data);
        
        const findings = this.generateFindings('fact', claimsAnalyzed, claimsVerified);
        const findingsEl = document.getElementById('factCheckerFindings');
        if (findingsEl) findingsEl.innerHTML = findings;
        
        const interpretation = this.generateInterpretation('fact', verificationScore);
        const interpEl = document.getElementById('factCheckerInterpretation');
        if (interpEl) interpEl.textContent = interpretation;
    }

    displayTransparencyAnalysis(data) {
        const sourcesCited = data.source_count || 0;
        const quotesUsed = data.quote_count || 0;
        
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
        
        const findings = this.generateFindings('transparency', sourcesCited, quotesUsed, transparencyScore);
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
        
        const findings = this.generateFindings('manipulation', manipulationScore, techniques, emotionalCount);
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
        
        const aiInsights = openaiData?.summary || '';
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
                        <h5>AI-Generated Analysis</h5>
                        <p>${aiInsights}</p>
                        ${keyPoints.length > 0 ? `
                            <h5>Key Insights</h5>
                            <ul>${keyPoints.map(point => `<li>${point}</li>`).join('')}</ul>
                        ` : ''}
                    </div>
                `;
            }
        }
        
        const findings = this.generateFindings('content', qualityScore, readability);
        const findingsEl = document.getElementById('contentAnalyzerFindings');
        if (findingsEl) findingsEl.innerHTML = findings;
        
        const interpretation = this.generateInterpretation('content', qualityScore);
        const interpEl = document.getElementById('contentAnalyzerInterpretation');
        if (interpEl) interpEl.textContent = interpretation;
    }

    displayAuthorAnalysis(data, fallbackAuthor) {
        const authorName = data.author_name || data.name || fallbackAuthor || 'Unknown';
        const authorScore = data.score || 0;
        const authorPosition = data.position || 'Writer';
        const authorBio = data.bio || '';
        
        document.getElementById('authorName').textContent = authorName;
        document.getElementById('authorPosition').textContent = authorPosition;
        document.getElementById('authorCredibilityScore').textContent = authorScore > 0 ? `${authorScore}/100` : 'N/A';
        
        if (authorBio) {
            document.getElementById('authorBio').style.display = 'block';
            document.getElementById('authorBioText').textContent = authorBio;
        }
        
        const profiles = this.extractAuthorProfiles(data);
        this.displayAuthorProfiles(profiles);
        
        const publications = data.recent_articles || [];
        this.displayPublicationHistory(publications);
        
        document.getElementById('articleCount').textContent = publications.length || 0;
        document.getElementById('profilesCount').textContent = Object.keys(profiles).length || 0;
        document.getElementById('awardsCount').textContent = data.awards?.length || 0;
    }

    generateFindings(type, ...args) {
        let content = '<div class="service-analysis-section">';
        content += '<div class="analysis-block">';
        content += '<h4><i class="fas fa-search"></i> What We Analyzed</h4>';
        content += '<p>We examined key indicators for this analysis.</p>';
        content += '</div>';
        content += '<div class="analysis-block">';
        content += '<h4><i class="fas fa-clipboard-check"></i> What We Found</h4>';
        content += '<p>';
        
        switch(type) {
            case 'credibility':
                const [score, rating, bias] = args;
                content += `Score: ${score}/100, Rating: ${rating}, Bias: ${bias}`;
                break;
            case 'bias':
                const [biasScore, lean, dominant] = args;
                content += `Bias Score: ${biasScore}/100, Political Lean: ${lean}`;
                break;
            case 'fact':
                const [analyzed, verified] = args;
                content += `${verified} of ${analyzed} claims verified`;
                break;
            case 'transparency':
                const [sources, quotes] = args;
                content += `${sources} sources cited, ${quotes} quotes used`;
                break;
            case 'manipulation':
                const [mScore, techniques, emotional] = args;
                content += `Score: ${mScore}/100, ${emotional} emotional terms`;
                break;
            case 'content':
                const [qScore, readability] = args;
                content += `Quality: ${qScore}/100, Readability: ${readability}`;
                break;
        }
        
        content += '</p></div>';
        content += '<div class="analysis-block">';
        content += '<h4><i class="fas fa-lightbulb"></i> What This Means</h4>';
        content += '<p>See interpretation below for details.</p>';
        content += '</div></div>';
        
        return content;
    }

    generateInterpretation(type, score, additional) {
        switch(type) {
            case 'credibility':
                if (score >= 80) return 'Highly credible source with strong reputation.';
                if (score >= 60) return 'Generally credible with some limitations.';
                if (score >= 40) return 'Mixed credibility - verify information.';
                return 'Low credibility - approach with caution.';
            
            case 'bias':
                if (score < 30) return 'Minimal bias detected - balanced reporting.';
                if (score < 50) return 'Moderate bias present - consider perspective.';
                if (score < 70) return 'Significant bias - seek alternative viewpoints.';
                return 'Heavy bias - primarily opinion/advocacy.';
            
            case 'fact':
                if (score >= 90) return 'Excellent fact accuracy.';
                if (score >= 70) return 'Good accuracy with minor issues.';
                if (score >= 50) return 'Mixed accuracy - verify claims.';
                return 'Poor accuracy - many unverified claims.';
            
            case 'transparency':
                if (score >= 80) return 'Excellent transparency and sourcing.';
                if (score >= 60) return 'Good transparency practices.';
                if (score >= 40) return 'Limited transparency.';
                return 'Poor transparency - sources unclear.';
            
            case 'manipulation':
                if (score < 30) return 'Minimal manipulation detected.';
                if (score < 50) return 'Some persuasive techniques used.';
                if (score < 70) return 'Significant manipulation present.';
                return 'Heavy manipulation - be very cautious.';
            
            case 'content':
                if (score >= 80) return 'Excellent content quality.';
                if (score >= 60) return 'Good quality with minor issues.';
                if (score >= 40) return 'Fair quality - some problems.';
                return 'Poor quality - significant issues.';
            
            default:
                return 'Analysis completed.';
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

    displayClaimsList(data) {
        const section = document.getElementById('claimsCheckedSection');
        const list = document.getElementById('verifiedClaimsList');
        
        if (!section || !list) return;
        
        const claims = data.claims || [];
        
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
                    <div class="claim-text">${claim.text || 'Claim checked'}</div>
                `;
                
                list.appendChild(claimEl);
            });
        } else {
            section.style.display = 'none';
        }
    }

    extractAuthorProfiles(data) {
        const profiles = {};
        if (data.linkedin_profile) profiles.linkedin = data.linkedin_profile;
        if (data.twitter_profile) profiles.twitter = data.twitter_profile;
        if (data.wikipedia_page) profiles.wikipedia = data.wikipedia_page;
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
                    link.innerHTML = `<i class="fab fa-${platform}"></i> ${platform}`;
                    profilesGrid.appendChild(link);
                }
            });
        }
    }

    displayPublicationHistory(publications) {
        const section = document.getElementById('publicationSection');
        const list = document.getElementById('publicationList');
        
        if (!section || !list) return;
        
        if (publications.length > 0) {
            section.style.display = 'block';
            list.innerHTML = '';
            
            publications.slice(0, 5).forEach(pub => {
                const pubEl = document.createElement('div');
                pubEl.className = 'publication-item';
                pubEl.innerHTML = `<div class="pub-title">${pub.title || 'Untitled'}</div>`;
                list.appendChild(pubEl);
            });
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
                detailed_analysis_keys: data.detailed_analysis ? Object.keys(data.detailed_analysis) : []
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

// Export for use
window.TruthLensAnalyzer = TruthLensAnalyzer;
