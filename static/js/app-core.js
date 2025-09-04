/**
 * TruthLens News Analyzer - Core Application
 * Part 1: Main class and essential functionality
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

        this.sourceTrendHistory = {};
        
        this.init();
        this.createServiceCards();
        this.initializeSourceRankings();
    }

    init() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.resetBtn.addEventListener('click', this.handleReset.bind(this));
        
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
        const existingRankings = document.getElementById('sourceRankings');
        if (!existingRankings) {
            this.createSourceRankingsSection();
        }
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
                ${window.ServiceTemplates ? window.ServiceTemplates.getTemplate(service.id) : '<div>Loading...</div>'}
            </div>
        `;
        
        return dropdown;
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
        if (rankingsContainer) {
            rankingsContainer.style.display = 'none';
        }
        
        const plagiarismDropdown = document.getElementById('plagiarismDetectorDropdown');
        if (plagiarismDropdown) {
            plagiarismDropdown.style.display = 'none';
        }
        
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
        
        const summaryEl = document.getElementById('articleSummary');
        if (summaryEl) summaryEl.textContent = 
            articleSummary.length > 100 ? articleSummary.substring(0, 100) + '...' : articleSummary;
        
        const sourceEl = document.getElementById('articleSource');
        if (sourceEl) sourceEl.textContent = source;
        
        const authorEl = document.getElementById('articleAuthor');
        if (authorEl) authorEl.textContent = author;
        
        const findingsEl = document.getElementById('findingsSummary');
        if (findingsEl) findingsEl.textContent = findingsSummary;
        
        // Use display methods from ServiceTemplates
        if (window.ServiceTemplates && window.ServiceTemplates.displayAllAnalyses) {
            window.ServiceTemplates.displayAllAnalyses(data, this);
        }
        
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

    // Source Rankings Methods
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
                    if (key === domain) {
                        data.isCurrent = true;
                    }
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

        if (data.isCurrent) {
            item.classList.add('highlight');
        }

        item.addEventListener('click', () => {
            this.showSourceDetails(domain, data);
        });

        return item;
    }

    updateSourceRankings(analysisResults) {
        const rankingsContainer = document.getElementById('sourceRankings');
        if (rankingsContainer) {
            rankingsContainer.style.display = 'block';
        }
        
        const currentSource = analysisResults.source || null;
        const currentScore = analysisResults.trust_score || 
                           analysisResults.detailed_analysis?.source_credibility?.score || 
                           0;
        
        this.displaySourceRankings(currentSource, currentScore);

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
        console.log('Source details:', domain, data);
    }

    // Utility functions
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

    showDebugInfo(data) {
        const debugInfo = document.getElementById('debugInfo');
        const debugData = document.getElementById('debugData');
        
        if (debugInfo && debugData && 
            (window.location.hostname === 'localhost' || 
             window.location.hostname.includes('render') ||
             window.location.hostname.includes('onrender'))) {
            
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
            if (loading) {
                loadingOverlay.classList.add('active');
            } else {
                loadingOverlay.classList.remove('active');
            }
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

// Export for use
window.TruthLensAnalyzer = TruthLensAnalyzer;
