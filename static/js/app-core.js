/**
 * TruthLens News Analyzer - App Core Module (RANKINGS DISPLAY REMOVED ONLY)
 * Date: September 10, 2025
 * Last Updated: September 10, 2025
 * 
 * FIXES IMPLEMENTED:
 * - Removed displaySourceRankings() method
 * - Removed createSourceRankingsSection() method  
 * - Removed initializeSourceRankings() call
 * - Removed ranking display methods ONLY
 * - KEPT all other functionality intact
 * 
 * NOTES:
 * - All dropdowns still work
 * - All services functional
 * - Only removed the duplicate rankings display
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

        this.sourceTrendHistory = {};
        this.init();
        this.createServiceCards();
    }

    cleanAuthorName(authorString) {
        if (!authorString || typeof authorString !== 'string') {
            return 'Unknown Author';
        }

        let cleaned = authorString;
        cleaned = cleaned.replace(/^by\s*/i, '');

        if (cleaned.includes('|')) {
            const parts = cleaned.split('|');
            cleaned = parts[0].trim();
        }

        cleaned = cleaned.replace(/\S+@\S+\.\S+/g, '').trim();
        cleaned = cleaned.replace(/\b(UPDATED|PUBLISHED|POSTED|MODIFIED):\s*.*/gi, '').trim();

        const orgPatterns = [
            /\s*(Chicago Tribune|New York Times|Washington Post|CNN|Fox News|Reuters|Associated Press|AP|BBC|NPR).*/gi,
            /\s*,\s*(Reporter|Writer|Journalist|Editor|Correspondent|Staff Writer|Contributing Writer).*/gi
        ];
        
        for (const pattern of orgPatterns) {
            cleaned = cleaned.replace(pattern, '');
        }

        cleaned = cleaned.replace(/\s*(Staff|Wire|Service|Report)$/gi, '');
        cleaned = cleaned.replace(/\s+/g, ' ').trim();
        cleaned = cleaned.replace(/[,;:\-|]+$/, '').trim();

        if (!cleaned || cleaned.length < 2 || /^[^a-zA-Z]+$/.test(cleaned)) {
            return 'Unknown Author';
        }

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
        
        const debugInfo = document.getElementById('debugInfo');
        if (debugInfo) {
            debugInfo.remove();
        }
        
        let trustScore = data.trust_score || 0;
        let articleSummary = data.article_summary || 'Analysis completed';
        let source = data.source || 'Unknown Source';
        
        let rawAuthor = data.author || 'Staff Writer';
        let cleanedAuthor = this.cleanAuthorName(rawAuthor);
        
        data.author = cleanedAuthor;
        
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
        
        const summaryEl = document.getElementById('articleSummary');
        if (summaryEl) {
            summaryEl.textContent = articleSummary.length > 100 ? 
                articleSummary.substring(0, 100) + '...' : articleSummary;
        }
        
        const sourceEl = document.getElementById('articleSource');
        if (sourceEl) sourceEl.textContent = source;
        
        const authorEl = document.getElementById('articleAuthor');
        if (authorEl) authorEl.textContent = cleanedAuthor;
        
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
        
        this.cleanupUnwantedText();
        
        if (typeof updateEnhancedTrustDisplay === 'function') {
            updateEnhancedTrustDisplay(data);
            setTimeout(() => {
                const findingsEl = document.getElementById('findingsSummary');
                if (findingsEl && findingsEl.textContent !== findingsSummary) {
                    findingsEl.textContent = findingsSummary;
                }
                this.cleanupUnwantedText();
            }, 100);
        }
        
        // Store current analysis info for ServiceTemplates to use
        if (window.ServiceTemplates) {
            window.currentAnalysisSource = source;
            window.currentAnalysisScore = trustScore;
        }
        
        if (window.ServiceTemplates && window.ServiceTemplates.displayAllAnalyses) {
            window.ServiceTemplates.displayAllAnalyses(data, this);
        } else {
            console.warn('ServiceTemplates not fully loaded, retrying...');
            setTimeout(() => {
                if (window.ServiceTemplates && window.ServiceTemplates.displayAllAnalyses) {
                    window.ServiceTemplates.displayAllAnalyses(data, this);
                } else {
                    console.error('ServiceTemplates failed to load');
                }
            }, 500);
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
            'bbc.co.uk': 'BBC News',
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
            'breitbart.com': 'Breitbart',
            'nbcnews.com': 'NBC News',
            'abcnews.go.com': 'ABC News',
            'cbsnews.com': 'CBS News',
            'usatoday.com': 'USA Today',
            'bloomberg.com': 'Bloomberg',
            'businessinsider.com': 'Business Insider',
            'vox.com': 'Vox',
            'slate.com': 'Slate',
            'salon.com': 'Salon',
            'huffpost.com': 'HuffPost',
            'buzzfeednews.com': 'BuzzFeed News',
            'vice.com': 'Vice News',
            'motherjones.com': 'Mother Jones',
            'thedailybeast.com': 'The Daily Beast',
            'newsweek.com': 'Newsweek',
            'time.com': 'TIME'
        };
        
        return nameMap[domain] || domain.replace('.com', '').replace('.org', '').replace('.net', '')
            .split('.')[0]
            .split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }

    showDebugInfo(data) {
        // Debug info disabled in production
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
        
        // Toggle display of content
        if (content.style.display === 'none' || content.style.display === '') {
            content.style.display = 'block';
        } else {
            content.style.display = 'none';
        }
        
        // Toggle chevron icon
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

// Export for global access
window.TruthLensAnalyzer = TruthLensAnalyzer;
