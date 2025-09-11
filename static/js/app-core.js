/**
 * TruthLens News Analyzer - SIMPLIFIED FIX
 * Date: September 11, 2025
 * Last Updated: September 11, 2025
 * 
 * SIMPLE FIX:
 * - Store full response data globally
 * - Repopulate dropdowns every time they're clicked
 * - No complex state management
 */

// Store analysis data globally
window.analysisData = null;

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
            <div class="service-content" id="${service.id}Content" style="display: none;">
                <!-- Content will be populated when dropdown is clicked -->
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
            
            // Store data globally
            window.analysisData = data;
            console.log('Analysis data stored:', data);
            
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
        window.analysisData = null;
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
            findingsEl.textContent = findingsSummary;
        }
        
        if (typeof updateEnhancedTrustDisplay === 'function') {
            updateEnhancedTrustDisplay(data);
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

// SIMPLIFIED dropdown toggle - populate on every click
window.toggleServiceDropdown = function(serviceId) {
    const dropdown = document.getElementById(`${serviceId}Dropdown`);
    const content = document.getElementById(`${serviceId}Content`);
    const toggle = dropdown?.querySelector('.service-toggle i');
    
    if (!dropdown || !content) return;
    
    dropdown.classList.toggle('active');
    
    if (content.style.display === 'none' || content.style.display === '') {
        content.style.display = 'block';
        
        // Always populate the content when opening
        if (window.analysisData && window.ServiceTemplates) {
            // Get template and populate it
            content.innerHTML = window.ServiceTemplates.getTemplate(serviceId);
            
            // Immediately populate with data
            const detailed = window.analysisData.detailed_analysis || {};
            
            switch(serviceId) {
                case 'sourceCredibility':
                    window.ServiceTemplates.displaySourceCredibility(detailed.source_credibility || {});
                    break;
                case 'biasDetector':
                    window.ServiceTemplates.displayBiasDetection(detailed.bias_detector || {});
                    break;
                case 'factChecker':
                    window.ServiceTemplates.displayFactChecking(detailed.fact_checker || {});
                    break;
                case 'transparencyAnalyzer':
                    window.ServiceTemplates.displayTransparencyAnalysis(detailed.transparency_analyzer || {});
                    break;
                case 'manipulationDetector':
                    window.ServiceTemplates.displayManipulationDetection(detailed.manipulation_detector || {});
                    break;
                case 'contentAnalyzer':
                    window.ServiceTemplates.displayContentAnalysis(
                        detailed.content_analyzer || {}, 
                        detailed.openai_enhancer || {}
                    );
                    break;
                case 'author':
                    window.ServiceTemplates.displayAuthorAnalysis(
                        detailed.author_analyzer || {}, 
                        window.analysisData.author
                    );
                    break;
            }
        } else {
            content.innerHTML = '<div style="padding: 2rem; text-align: center; color: #666;">No analysis data available. Please analyze an article first.</div>';
        }
    } else {
        content.style.display = 'none';
    }
    
    if (toggle) {
        toggle.classList.toggle('fa-chevron-down');
        toggle.classList.toggle('fa-chevron-up');
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    window.analyzer = new TruthLensAnalyzer();
});

window.TruthLensAnalyzer = TruthLensAnalyzer;
