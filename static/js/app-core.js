/**
 * TruthLens News Analyzer - App Core Module (COMPLETE FIXED VERSION)
 * Handles application control flow, user interactions, and API communication
 * FIXES: Added findings summary, compact source rankings, working filter buttons
 * CRITICAL FIXES: Rankings now visible, findings display properly, debug info hidden
 */

class TruthLensAnalyzer {
    constructor() {
        // Core elements
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

        // FIXED: Added proper categories for all sources
        this.sourceRankingsData = {
            'reuters.com': { score: 95, rank: 1, trend: 'stable', category: 'mainstream' },
            'ap.org': { score: 94, rank: 2, trend: 'up', category: 'mainstream' },
            'bbc.com': { score: 92, rank: 3, trend: 'stable', category: 'mainstream' },
            'npr.org': { score: 90, rank: 4, trend: 'stable', category: 'mainstream' },
            'propublica.org': { score: 88, rank: 5, trend: 'up', category: 'independent' },
            'wsj.com': { score: 85, rank: 6, trend: 'stable', category: 'mainstream' },
            'nytimes.com': { score: 84, rank: 7, trend: 'down', category: 'mainstream' },
            'ft.com': { score: 83, rank: 8, trend: 'stable', category: 'mainstream' },
            'economist.com': { score: 82, rank: 9, trend: 'stable', category: 'mainstream' },
            'washingtonpost.com': { score: 80, rank: 10, trend: 'down', category: 'mainstream' },
            'theguardian.com': { score: 79, rank: 11, trend: 'stable', category: 'mainstream' },
            'theintercept.com': { score: 77, rank: 12, trend: 'up', category: 'independent' },
            'axios.com': { score: 76, rank: 13, trend: 'up', category: 'independent' },
            'politico.com': { score: 75, rank: 14, trend: 'up', category: 'mainstream' },
            'cnn.com': { score: 72, rank: 15, trend: 'stable', category: 'mainstream' },
            'foxnews.com': { score: 70, rank: 16, trend: 'stable', category: 'mainstream' },
            'msnbc.com': { score: 68, rank: 17, trend: 'down', category: 'mainstream' },
            'thehill.com': { score: 65, rank: 18, trend: 'stable', category: 'mainstream' },
            'dailywire.com': { score: 63, rank: 19, trend: 'stable', category: 'independent' },
            'breitbart.com': { score: 60, rank: 20, trend: 'down', category: 'independent' }
        };

        this.currentFilter = 'all';
        this.sourceTrendHistory = {};
        this.lastAnalyzedSource = null;
        this.lastAnalyzedScore = null;
        
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

        // Find the trust score overview section
        const overviewSection = resultsSection.querySelector('.analysis-overview');
        if (!overviewSection) return;

        // Check if rankings already exist
        if (document.getElementById('sourceRankings')) return;

        // Create compact rankings HTML
        const rankingsDiv = document.createElement('div');
        rankingsDiv.id = 'sourceRankings';
        rankingsDiv.className = 'source-rankings-compact';
        rankingsDiv.style.display = 'none';
        rankingsDiv.innerHTML = `
            <div class="rankings-header-compact">
                <h4 class="rankings-title-compact">
                    <i class="fas fa-trophy"></i> Source Rankings
                </h4>
                <div class="filter-buttons-compact">
                    <button class="filter-btn active" data-filter="all">All</button>
                    <button class="filter-btn" data-filter="mainstream">Mainstream</button>
                    <button class="filter-btn" data-filter="independent">Independent</button>
                </div>
            </div>
            <div class="rankings-chart-compact" id="rankingsChart"></div>
        `;
        
        // Insert after the overview section
        overviewSection.insertAdjacentElement('afterend', rankingsDiv);
        this.attachFilterListeners();
    }

    attachFilterListeners() {
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const filter = e.target.dataset.filter;
                this.filterSources(filter);
            });
        });
    }

    filterSources(filter) {
        this.currentFilter = filter;
        
        // Update active button
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.filter === filter) {
                btn.classList.add('active');
            }
        });
        
        // Redisplay with filter
        this.displaySourceRankings(this.lastAnalyzedSource, this.lastAnalyzedScore);
    }

    createServiceCards() {
        if (!this.serviceContainer) return;
        
        this.serviceContainer.innerHTML = '';
        this.services.forEach(service => {
            const dropdown = this.createServiceDropdown(service);
            this.serviceContainer.appendChild(dropdown);
        });
    }

    createServiceDropdown(service) {
        const dropdown = document.createElement('div');
        dropdown.className = `service-dropdown ${service.id}Dropdown`;
        dropdown.id = `${service.id}Dropdown`;
        
        dropdown.innerHTML = `
            <div class="service-header" onclick="toggleServiceDropdown('${service.id}')">
                <div class="service-title">
                    <i class="fas ${service.icon}"></i>
                    <span>${service.name}</span>
                </div>
                <div class="service-toggle">
                    <i class="fas fa-chevron-down"></i>
                </div>
            </div>
            <div class="service-content" id="${service.id}Content">
                ${window.ServiceTemplates ? window.ServiceTemplates.getTemplate(service.id) : ''}
            </div>
        `;
        
        return dropdown;
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const url = this.urlInput.value.trim();
        const text = this.textInput.value.trim();
        
        if (!url && !text) {
            alert('Please enter a URL or paste article text');
            return;
        }
        
        this.setLoading(true);
        this.showProgress();
        
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, text })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Analysis failed');
            }
            
            this.displayResults(data);
            
        } catch (error) {
            console.error('Error:', error);
            alert('Error analyzing article: ' + error.message);
            this.hideProgress();
        } finally {
            this.setLoading(false);
        }
    }

    handleReset() {
        this.form.reset();
        this.resultsSection.classList.remove('show');
        this.progressContainer.classList.remove('active');
        this.lastAnalyzedSource = null;
        this.lastAnalyzedScore = null;
        this.currentFilter = 'all';
        
        const sourceRankings = document.getElementById('sourceRankings');
        if (sourceRankings) {
            sourceRankings.style.display = 'none';
        }
    }

    showProgress() {
        this.progressContainer.classList.add('active');
        this.animateProgress();
    }

    hideProgress() {
        this.progressContainer.classList.remove('active');
    }

    animateProgress() {
        let progress = 0;
        const totalSteps = 7;
        let currentStep = 0;
        
        const interval = setInterval(() => {
            progress += Math.random() * 15 + 5;
            
            if (progress > (currentStep + 1) * (100 / totalSteps)) {
                this.setStepActive(currentStep);
                currentStep++;
                
                if (currentStep > 0) {
                    this.setStepCompleted(currentStep - 1);
                }
            }
            
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                
                this.setStepCompleted(currentStep - 1);
                this.setStepActive(currentStep);
                
                setTimeout(() => {
                    this.setStepCompleted(currentStep);
                }, 500);
            }
            
            this.progressBar.style.width = `${progress}%`;
            this.progressPercentage.textContent = `${Math.round(progress)}%`;
        }, 800);
    }

    setStepActive(stepIndex) {
        const step = this.progressSteps?.querySelector(`[data-step="${stepIndex}"]`);
        if (step) {
            step.classList.add('active');
            const icon = step.querySelector('.step-icon');
            if (icon) icon.innerHTML = '<div class="spinner"></div>';
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
        
        // CRITICAL: Remove ALL debug info elements completely
        const debugInfo = document.getElementById('debugInfo');
        if (debugInfo) {
            debugInfo.remove(); // Remove it entirely from DOM
        }
        
        let trustScore = data.trust_score || 0;
        let articleSummary = data.article_summary || 'Analysis completed';
        let source = data.source || 'Unknown Source';
        let author = data.author || 'Staff Writer';
        
        // Store for rankings
        this.lastAnalyzedSource = source;
        this.lastAnalyzedScore = trustScore;
        
        // CRITICAL FIX: Generate proper findings summary
        let findingsSummary = '';
        const trustLevel = trustScore >= 80 ? 'high' : trustScore >= 60 ? 'good' : trustScore >= 40 ? 'moderate' : 'low';
        
        switch(trustLevel) {
            case 'high':
                findingsSummary = "This article demonstrates high credibility and trustworthiness. The source is well-established and reputable. Content appears balanced and factually accurate.";
                break;
            case 'good':
                findingsSummary = "This article shows generally good credibility with some minor areas of concern. The source is reasonably reputable and content appears mostly balanced.";
                break;
            case 'moderate':
                findingsSummary = "This article has moderate credibility with several issues identified. Source credibility is mixed and some bias may be present. Fact-checking revealed unverified claims.";
                break;
            case 'low':
                findingsSummary = "This article shows significant credibility concerns. Source reputation is questionable, notable bias detected, and multiple claims could not be verified.";
                break;
        }
        
        // Add specific details if available
        if (data.detailed_analysis) {
            const d = data.detailed_analysis;
            if (d.bias_detector?.bias_score !== undefined) {
                const biasLevel = d.bias_detector.bias_score;
                if (biasLevel < 30) {
                    findingsSummary += " The content shows minimal bias.";
                } else if (biasLevel > 70) {
                    findingsSummary += " Significant bias was detected in the presentation.";
                }
            }
            if (d.fact_checker?.accuracy_score === 0) {
                findingsSummary += " No claims could be independently verified.";
            }
        }
        
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
        
        // Update basic info
        const summaryEl = document.getElementById('articleSummary');
        if (summaryEl) {
            summaryEl.textContent = articleSummary.length > 100 ? 
                articleSummary.substring(0, 100) + '...' : articleSummary;
        }
        
        const sourceEl = document.getElementById('articleSource');
        if (sourceEl) sourceEl.textContent = source;
        
        const authorEl = document.getElementById('articleAuthor');
        if (authorEl) authorEl.textContent = author;
        
        // CRITICAL FIX: Force update findings with inline styles to override everything
        const findingsEl = document.getElementById('findingsSummary');
        if (findingsEl) {
            // Clear any existing content first
            findingsEl.innerHTML = '';
            // Set the new content
            findingsEl.textContent = findingsSummary;
            // Force visibility with !important styles
            findingsEl.setAttribute('style', `
                display: block !important;
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
                border-left: 3px solid #3b82f6 !important;
                padding: 12px 15px !important;
                border-radius: 6px !important;
                margin-top: 15px !important;
                color: #475569 !important;
                line-height: 1.6 !important;
                font-size: 0.95rem !important;
                visibility: visible !important;
                opacity: 1 !important;
            `);
        }
        
        // Update the enhanced trust display that's defined in your HTML
        if (typeof updateEnhancedTrustDisplay === 'function') {
            // This function is defined in your HTML, let it run first
            updateEnhancedTrustDisplay(data);
            // Then override the findings again to ensure our text stays
            setTimeout(() => {
                const findingsEl = document.getElementById('findingsSummary');
                if (findingsEl && findingsEl.textContent !== findingsSummary) {
                    findingsEl.textContent = findingsSummary;
                }
            }, 100);
        }
        
        // CRITICAL FIX: Ensure source rankings display
        setTimeout(() => {
            this.displaySourceRankings(source, trustScore);
        }, 200);
        
        // Use display methods from ServiceTemplates
        if (window.ServiceTemplates && window.ServiceTemplates.displayAllAnalyses) {
            window.ServiceTemplates.displayAllAnalyses(data, this);
        }
        
        this.showResults();
    }

    // FIXED: Generate a proper findings summary if not provided
    generateFindingsSummary(data) {
        const trustScore = data.trust_score || 0;
        const detailed = data.detailed_analysis || {};
        
        let summary = [];
        
        // Trust score assessment
        if (trustScore >= 80) {
            summary.push("This article demonstrates high credibility and trustworthiness.");
        } else if (trustScore >= 60) {
            summary.push("This article shows generally good credibility with some areas of concern.");
        } else if (trustScore >= 40) {
            summary.push("This article has moderate credibility with several issues identified.");
        } else {
            summary.push("This article shows significant credibility concerns.");
        }
        
        // Add specific findings from services
        if (detailed.source_credibility?.score >= 80) {
            summary.push("The source is highly reputable and well-established.");
        } else if (detailed.source_credibility?.score < 50) {
            summary.push("Source credibility is questionable.");
        }
        
        if (detailed.bias_detector?.bias_score > 70) {
            summary.push("Significant bias detected in the content.");
        } else if (detailed.bias_detector?.bias_score < 30) {
            summary.push("Content appears relatively unbiased and balanced.");
        }
        
        if (detailed.fact_checker?.accuracy_score >= 80) {
            summary.push("Claims are well-supported by evidence.");
        } else if (detailed.fact_checker?.accuracy_score < 50) {
            summary.push("Multiple unverified or false claims detected.");
        }
        
        if (detailed.manipulation_detector?.manipulation_score > 60) {
            summary.push("Warning: Potential manipulation techniques detected.");
        }
        
        return summary.join(" ");
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

    // FIXED: Compact source rankings with filter support - FORCE DISPLAY
    displaySourceRankings(currentSource = null, currentScore = null) {
        // Create rankings if they don't exist
        let rankingsContainer = document.getElementById('sourceRankings');
        if (!rankingsContainer) {
            this.createSourceRankingsSection();
            rankingsContainer = document.getElementById('sourceRankings');
        }
        
        const rankingsChart = document.getElementById('rankingsChart');
        if (!rankingsContainer || !rankingsChart) return;

        // CRITICAL: Force visibility
        rankingsContainer.style.display = 'block';
        rankingsContainer.style.visibility = 'visible';
        rankingsContainer.style.opacity = '1';
        rankingsChart.innerHTML = '';

        // Filter sources based on current filter
        let rankingsToDisplay = Object.entries(this.sourceRankingsData)
            .filter(([domain, data]) => {
                if (this.currentFilter === 'all') return true;
                return data.category === this.currentFilter;
            })
            .sort((a, b) => b[1].score - a[1].score)
            .slice(0, 5); // Show only top 5 for compact display

        // Add or mark current source
        if (currentSource && currentScore !== null) {
            const domain = this.extractDomain(currentSource);
            const existingIndex = rankingsToDisplay.findIndex(([d]) => d === domain);
            
            if (existingIndex >= 0) {
                // Mark existing source as current
                rankingsToDisplay[existingIndex][1].isCurrent = true;
            } else {
                // Add new source if not in top 5
                const category = this.guessCategory(domain);
                if (this.currentFilter === 'all' || category === this.currentFilter) {
                    const newEntry = [
                        domain,
                        {
                            score: currentScore,
                            rank: this.calculateRank(currentScore),
                            trend: 'new',
                            category: category,
                            isCurrent: true
                        }
                    ];
                    rankingsToDisplay.push(newEntry);
                    rankingsToDisplay.sort((a, b) => b[1].score - a[1].score);
                    rankingsToDisplay = rankingsToDisplay.slice(0, 5);
                }
            }
        }

        // Create compact ranking items
        rankingsToDisplay.forEach(([domain, data], index) => {
            const rankItem = this.createCompactRankingItem(domain, data, index);
            rankingsChart.appendChild(rankItem);
        });

        // Add "show more" option if there are more sources
        const totalInCategory = Object.values(this.sourceRankingsData)
            .filter(data => this.currentFilter === 'all' || data.category === this.currentFilter)
            .length;
        
        if (totalInCategory > 5) {
            const showMore = document.createElement('div');
            showMore.className = 'show-more-sources';
            showMore.innerHTML = `<span>+${totalInCategory - 5} more sources</span>`;
            rankingsChart.appendChild(showMore);
        }

        // Animate in
        setTimeout(() => {
            rankingsChart.querySelectorAll('.ranking-item-compact').forEach((item, index) => {
                setTimeout(() => {
                    item.classList.add('animate-in');
                }, index * 30);
            });
        }, 100);
    }

    createCompactRankingItem(domain, data, index) {
        const item = document.createElement('div');
        const trustClass = this.getScoreCategory(data.score);
        item.className = `ranking-item-compact ${trustClass} ${data.isCurrent ? 'current-source' : ''}`;
        
        const trendIcon = this.getTrendIcon(data.trend);
        
        item.innerHTML = `
            <div class="rank-number">#${index + 1}</div>
            <div class="source-name-compact">${this.formatDomainName(domain)}</div>
            <div class="score-bar-compact">
                <div class="score-fill" style="width: ${data.score}%"></div>
            </div>
            <div class="score-value">${data.score}</div>
            <div class="trend-icon">${trendIcon}</div>
            ${data.isCurrent ? '<span class="current-badge">CURRENT</span>' : ''}
        `;
        
        return item;
    }

    guessCategory(domain) {
        // List of known mainstream domains
        const mainstream = ['cnn', 'fox', 'nbc', 'cbs', 'abc', 'nytimes', 'wsj', 'washingtonpost', 
                          'usatoday', 'bbc', 'guardian', 'reuters', 'ap.org', 'npr', 'politico', 'thehill'];
        
        const domainLower = domain.toLowerCase();
        for (const ms of mainstream) {
            if (domainLower.includes(ms)) {
                return 'mainstream';
            }
        }
        return 'independent';
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
            'theguardian.com': 'The Guardian',
            'theintercept.com': 'The Intercept',
            'cnn.com': 'CNN',
            'foxnews.com': 'Fox News',
            'msnbc.com': 'MSNBC',
            'politico.com': 'Politico',
            'axios.com': 'Axios',
            'thehill.com': 'The Hill',
            'dailywire.com': 'Daily Wire',
            'breitbart.com': 'Breitbart'
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
            'up': '<i class="fas fa-arrow-up" style="color: #10b981;"></i>',
            'down': '<i class="fas fa-arrow-down" style="color: #ef4444;"></i>',
            'stable': '<i class="fas fa-minus" style="color: #6b7280;"></i>',
            'new': '<i class="fas fa-star" style="color: #f59e0b;"></i>'
        };
        return icons[trend] || icons['stable'];
    }

    showDebugInfo(data) {
        // COMPLETELY DISABLED - No debug info in any environment
        return;
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
                '<i class="fas fa-spinner fa-spin"></i> Analyzing...' : 
                '<i class="fas fa-search"></i> Analyze Article';
        }
    }
}

// Global function for dropdowns
window.toggleServiceDropdown = function(serviceId) {
    const dropdown = document.getElementById(`${serviceId}Dropdown`);
    const content = document.getElementById(`${serviceId}Content`);
    const toggle = dropdown?.querySelector('.service-toggle i');
    
    if (dropdown && content) {
        dropdown.classList.toggle('active');
        if (toggle) {
            toggle.classList.toggle('fa-chevron-down');
            toggle.classList.toggle('fa-chevron-up');
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.analyzer = new TruthLensAnalyzer();
});
