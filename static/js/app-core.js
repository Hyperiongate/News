/**
 * TruthLens News Analyzer - App Core Module (FIXED VERSION)
 * Date: January 27, 2025
 * Last Updated: January 27, 2025
 * 
 * FIXES IMPLEMENTED:
 * - Removed duplicate Source Credibility Rankings
 * - Added source icons to compact ranking items
 * - Using logos from the upper ranking design in lower ranking
 * - Single unified source rankings display
 * 
 * NOTES:
 * - Only one Source Rankings section is created and displayed
 * - Icons are color-coded per source for brand recognition
 * - Compact ranking chart includes all visual elements
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

        // Enhanced source rankings data with colors and icons
        this.sourceRankingsData = {
            'reuters.com': { score: 95, rank: 1, trend: 'stable', category: 'mainstream', color: '#FF6B00', icon: 'RE' },
            'ap.org': { score: 94, rank: 2, trend: 'up', category: 'mainstream', color: '#FF0000', icon: 'AP' },
            'bbc.com': { score: 92, rank: 3, trend: 'stable', category: 'mainstream', color: '#000000', icon: 'BB' },
            'npr.org': { score: 90, rank: 4, trend: 'stable', category: 'mainstream', color: '#0066CC', icon: 'NP' },
            'propublica.org': { score: 88, rank: 5, trend: 'up', category: 'independent', color: '#2E7D32', icon: 'PP' },
            'wsj.com': { score: 85, rank: 6, trend: 'stable', category: 'mainstream', color: '#1976D2', icon: 'WS' },
            'nytimes.com': { score: 84, rank: 7, trend: 'down', category: 'mainstream', color: '#000000', icon: 'NY' },
            'ft.com': { score: 83, rank: 8, trend: 'stable', category: 'mainstream', color: '#FFA000', icon: 'FT' },
            'economist.com': { score: 82, rank: 9, trend: 'stable', category: 'mainstream', color: '#E53935', icon: 'EC' },
            'washingtonpost.com': { score: 80, rank: 10, trend: 'down', category: 'mainstream', color: '#1565C0', icon: 'WP' },
            'theguardian.com': { score: 79, rank: 11, trend: 'stable', category: 'mainstream', color: '#052962', icon: 'GU' },
            'theintercept.com': { score: 77, rank: 12, trend: 'up', category: 'independent', color: '#7B1FA2', icon: 'TI' },
            'axios.com': { score: 76, rank: 13, trend: 'up', category: 'independent', color: '#00796B', icon: 'AX' },
            'politico.com': { score: 75, rank: 14, trend: 'up', category: 'mainstream', color: '#DC143C', icon: 'PO' },
            'cnn.com': { score: 72, rank: 15, trend: 'stable', category: 'mainstream', color: '#CC0000', icon: 'CN' },
            'foxnews.com': { score: 70, rank: 16, trend: 'stable', category: 'mainstream', color: '#003366', icon: 'FX' },
            'msnbc.com': { score: 68, rank: 17, trend: 'down', category: 'mainstream', color: '#0089D0', icon: 'MS' },
            'thehill.com': { score: 65, rank: 18, trend: 'stable', category: 'mainstream', color: '#006B3C', icon: 'TH' },
            'dailywire.com': { score: 63, rank: 19, trend: 'stable', category: 'independent', color: '#8B4513', icon: 'DW' },
            'breitbart.com': { score: 60, rank: 20, trend: 'down', category: 'independent', color: '#FF6600', icon: 'BB' }
        };

        this.currentFilter = 'all';
        this.sourceTrendHistory = {};
        this.lastAnalyzedSource = null;
        this.lastAnalyzedScore = null;
        
        this.init();
        this.createServiceCards();
        this.initializeSourceRankings();
    }

    /**
     * Clean author name from malformed strings
     */
    cleanAuthorName(authorString) {
        if (!authorString || typeof authorString !== 'string') {
            return 'Unknown Author';
        }

        let cleaned = authorString;

        // Remove "By" prefix (case insensitive)
        cleaned = cleaned.replace(/^by\s*/i, '');

        // Handle pipe-separated format (name|email|organization)
        if (cleaned.includes('|')) {
            const parts = cleaned.split('|');
            cleaned = parts[0].trim();
        }

        // Remove email addresses
        cleaned = cleaned.replace(/\S+@\S+\.\S+/g, '').trim();

        // Remove timestamps
        cleaned = cleaned.replace(/\b(UPDATED|PUBLISHED|POSTED|MODIFIED):\s*.*/gi, '').trim();

        // Remove organization names
        const orgPatterns = [
            /\s*(Chicago Tribune|New York Times|Washington Post|CNN|Fox News|Reuters|Associated Press|AP|BBC|NPR).*/gi,
            /\s*,\s*(Reporter|Writer|Journalist|Editor|Correspondent|Staff Writer|Contributing Writer).*/gi
        ];
        
        for (const pattern of orgPatterns) {
            cleaned = cleaned.replace(pattern, '');
        }

        // Remove common suffixes
        cleaned = cleaned.replace(/\s*(Staff|Wire|Service|Report)$/gi, '');

        // Clean up multiple spaces and trim
        cleaned = cleaned.replace(/\s+/g, ' ').trim();

        // Remove any remaining special characters at the end
        cleaned = cleaned.replace(/[,;:\-|]+$/, '').trim();

        // If we ended up with nothing or just special characters, return unknown
        if (!cleaned || cleaned.length < 2 || /^[^a-zA-Z]+$/.test(cleaned)) {
            return 'Unknown Author';
        }

        // Capitalize properly
        cleaned = cleaned.split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');

        return cleaned;
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

        const overviewSection = resultsSection.querySelector('.enhanced-analysis-overview');
        if (!overviewSection) return;

        // Don't create if it already exists
        if (document.getElementById('sourceRankings')) return;

        const rankingsDiv = document.createElement('div');
        rankingsDiv.id = 'sourceRankings';
        rankingsDiv.className = 'source-rankings-compact';
        rankingsDiv.style.display = 'none';
        rankingsDiv.innerHTML = `
            <div class="rankings-header-compact">
                <h4 class="rankings-title-compact">
                    <i class="fas fa-trophy"></i> News Source Credibility Rankings
                </h4>
                <div class="filter-buttons-compact">
                    <button class="filter-btn active" data-filter="all">All</button>
                    <button class="filter-btn" data-filter="mainstream">Mainstream</button>
                    <button class="filter-btn" data-filter="independent">Independent</button>
                </div>
            </div>
            <div class="rankings-chart-compact" id="rankingsChart"></div>
        `;
        
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
        
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.filter === filter) {
                btn.classList.add('active');
            }
        });
        
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
        
        // Remove debug info elements
        const debugInfo = document.getElementById('debugInfo');
        if (debugInfo) {
            debugInfo.remove();
        }
        
        let trustScore = data.trust_score || 0;
        let articleSummary = data.article_summary || 'Analysis completed';
        let source = data.source || 'Unknown Source';
        
        // Clean the author name
        let rawAuthor = data.author || 'Staff Writer';
        let cleanedAuthor = this.cleanAuthorName(rawAuthor);
        
        // Update data object with cleaned author
        data.author = cleanedAuthor;
        
        // Store for rankings
        this.lastAnalyzedSource = source;
        this.lastAnalyzedScore = trustScore;
        
        // Generate findings summary
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
            
            // Clean author name in detailed analysis
            if (d.author_analyzer) {
                if (d.author_analyzer.name) {
                    d.author_analyzer.name = this.cleanAuthorName(d.author_analyzer.name);
                }
                if (d.author_analyzer.author_name) {
                    d.author_analyzer.author_name = this.cleanAuthorName(d.author_analyzer.author_name);
                }
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
        if (authorEl) authorEl.textContent = cleanedAuthor;
        
        // Update findings
        const findingsEl = document.getElementById('findingsSummary');
        if (findingsEl) {
            findingsEl.innerHTML = '';
            findingsEl.textContent = findingsSummary;
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
        
        // Clean up any unwanted text
        this.cleanupUnwantedText();
        
        // Update enhanced trust display
        if (typeof updateEnhancedTrustDisplay === 'function') {
            updateEnhancedTrustDisplay(data);
            // Override findings again after HTML script runs
            setTimeout(() => {
                const findingsEl = document.getElementById('findingsSummary');
                if (findingsEl && findingsEl.textContent !== findingsSummary) {
                    findingsEl.textContent = findingsSummary;
                }
                this.cleanupUnwantedText();
            }, 100);
        }
        
        // Display source rankings
        setTimeout(() => {
            this.displaySourceRankings(source, trustScore);
        }, 200);
        
        // Use display methods from ServiceTemplates
        if (window.ServiceTemplates && window.ServiceTemplates.displayAllAnalyses) {
            window.ServiceTemplates.displayAllAnalyses(data, this);
        }
        
        this.showResults();
    }

    cleanupUnwantedText() {
        const overview = document.querySelector('.enhanced-analysis-overview');
        if (overview) {
            const walker = document.createTreeWalker(
                overview,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );
            
            let node;
            while (node = walker.nextNode()) {
                if (node.textContent.includes('Trust Score:') && 
                    node.textContent.includes('Fact Check:') &&
                    node.textContent.includes('|')) {
                    node.textContent = '';
                }
                if (node.textContent.includes('/100 (Medium)') ||
                    node.textContent.includes('% verified')) {
                    node.textContent = '';
                }
            }
        }
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

    displaySourceRankings(currentSource = null, currentScore = null) {
        let rankingsContainer = document.getElementById('sourceRankings');
        if (!rankingsContainer) {
            this.createSourceRankingsSection();
            rankingsContainer = document.getElementById('sourceRankings');
        }
        
        const rankingsChart = document.getElementById('rankingsChart');
        if (!rankingsContainer || !rankingsChart) return;

        rankingsContainer.style.display = 'block';
        rankingsContainer.style.visibility = 'visible';
        rankingsContainer.style.opacity = '1';
        rankingsChart.innerHTML = '';

        let rankingsToDisplay = Object.entries(this.sourceRankingsData)
            .filter(([domain, data]) => {
                if (this.currentFilter === 'all') return true;
                return data.category === this.currentFilter;
            })
            .sort((a, b) => b[1].score - a[1].score)
            .
