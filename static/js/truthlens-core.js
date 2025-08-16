// truthlens-core.js - Consolidated Core Application Logic
// Combines core functionality, state management, and API communication

// Global configuration
const CONFIG = {
    API_ENDPOINT: '/api/analyze',
    isPro: true,
    services: [
        { 
            id: 'source_credibility', 
            name: 'Source Credibility', 
            icon: 'fa-shield-alt', 
            weight: 0.25, 
            isPro: false,
            description: 'Evaluates the reliability and trustworthiness of the news source'
        },
        { 
            id: 'author_analyzer', 
            name: 'Author Analysis', 
            icon: 'fa-user-check', 
            weight: 0.20, 
            isPro: false,
            description: 'Analyzes author credentials and publishing history'
        },
        { 
            id: 'bias_detector', 
            name: 'Bias Detection', 
            icon: 'fa-balance-scale', 
            weight: 0.15, 
            isPro: true,
            description: 'Detects political, ideological, and other forms of bias'
        },
        { 
            id: 'fact_checker', 
            name: 'Fact Verification', 
            icon: 'fa-check-double', 
            weight: 0.20, 
            isPro: true,
            description: 'Verifies claims and statements against reliable sources'
        },
        { 
            id: 'transparency_analyzer', 
            name: 'Transparency Analysis', 
            icon: 'fa-eye', 
            weight: 0.10, 
            isPro: true,
            description: 'Evaluates disclosure of sources, funding, and conflicts of interest'
        },
        { 
            id: 'manipulation_detector', 
            name: 'Manipulation Detection', 
            icon: 'fa-mask', 
            weight: 0.10, 
            isPro: true,
            description: 'Identifies manipulation tactics and propaganda techniques'
        },
        { 
            id: 'content_analyzer', 
            name: 'Content Analysis', 
            icon: 'fa-file-alt', 
            weight: 0.05, 
            isPro: true,
            description: 'Analyzes writing quality, readability, and content structure'
        },
        { 
            id: 'plagiarism_detector', 
            name: 'Plagiarism Detection', 
            icon: 'fa-copy', 
            weight: 0.05, 
            isPro: true,
            description: 'Checks for copied content and proper attribution'
        }
    ]
};

// Main Application Class
class TruthLensApp {
    constructor() {
        this.state = {
            currentAnalysis: null,
            currentMetadata: null,
            isAnalyzing: false,
            currentTab: 'url',
            charts: {}
        };
        
        this.utils = new TruthLensUtils();
        this.display = null; // Will be initialized after TruthLensDisplay is defined
        this.services = null; // Will be initialized after TruthLensServices is defined
        
        this.init();
    }

    init() {
        // Wait for other classes to be defined
        if (typeof TruthLensDisplay !== 'undefined') {
            this.display = new TruthLensDisplay(this);
        }
        if (typeof TruthLensServices !== 'undefined') {
            this.services = new TruthLensServices(this);
        }
        
        this.setupEventListeners();
        console.log('TruthLens initialized');
    }

    setupEventListeners() {
        // URL/Text input handlers
        const urlInput = document.getElementById('urlInput');
        if (urlInput) {
            urlInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    window.truthLensApp.analyzeArticle();
                }
            });
        }
        
        const textInput = document.getElementById('textInput');
        if (textInput) {
            textInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && e.ctrlKey) {
                    window.truthLensApp.analyzeArticle();
                }
            });
        }
        
        // Button handlers
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', function() {
                window.truthLensApp.analyzeArticle();
            });
        }
        
        const analyzeTextBtn = document.getElementById('analyzeTextBtn');
        if (analyzeTextBtn) {
            analyzeTextBtn.addEventListener('click', function() {
                window.truthLensApp.analyzeArticle();
            });
        }
        
        const resetBtn = document.getElementById('resetBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                window.truthLensApp.resetAnalysis();
            });
        }
        
        const resetTextBtn = document.getElementById('resetTextBtn');
        if (resetTextBtn) {
            resetTextBtn.addEventListener('click', function() {
                window.truthLensApp.resetAnalysis();
            });
        }
        
        const downloadPdfBtn = document.getElementById('downloadPdfBtn');
        if (downloadPdfBtn) {
            downloadPdfBtn.addEventListener('click', function() {
                window.truthLensApp.downloadPDF();
            });
        }
        
        const shareResultsBtn = document.getElementById('shareResultsBtn');
        if (shareResultsBtn) {
            shareResultsBtn.addEventListener('click', function() {
                window.truthLensApp.shareResults();
            });
        }
        
        // Tab switching
        const modeBtns = document.querySelectorAll('.mode-btn');
        modeBtns.forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                const mode = e.currentTarget.getAttribute('data-mode');
                window.truthLensApp.switchTab(mode);
            });
        });
        
        // Example buttons
        const exampleBtns = document.querySelectorAll('.example-btn');
        exampleBtns.forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                const url = e.target.getAttribute('data-url');
                if (url) {
                    document.getElementById('urlInput').value = url;
                    window.truthLensApp.analyzeArticle();
                }
            });
        });
    }

    switchTab(mode) {
        this.state.currentTab = mode;
        
        const modeBtns = document.querySelectorAll('.mode-btn');
        modeBtns.forEach(function(btn) {
            if (btn.getAttribute('data-mode') === mode) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        ['url', 'text'].forEach(function(type) {
            const isActive = type === mode;
            const explanationEl = document.getElementById(type + 'Explanation');
            const inputWrapperEl = document.getElementById(type + 'InputWrapper');
            
            if (explanationEl) {
                if (isActive) {
                    explanationEl.classList.add('active');
                } else {
                    explanationEl.classList.remove('active');
                }
            }
            
            if (inputWrapperEl) {
                if (isActive) {
                    inputWrapperEl.classList.add('active');
                } else {
                    inputWrapperEl.classList.remove('active');
                }
            }
        });
    }

    resetAnalysis() {
        const urlInput = document.getElementById('urlInput');
        const textInput = document.getElementById('textInput');
        const resultsSection = document.getElementById('resultsSection');
        
        if (urlInput) urlInput.value = '';
        if (textInput) textInput.value = '';
        if (resultsSection) resultsSection.style.display = 'none';
        
        this.state.currentAnalysis = null;
        this.state.currentMetadata = null;
    }

    async analyzeArticle() {
        if (this.state.isAnalyzing) return;

        const urlInput = document.getElementById('urlInput');
        const textInput = document.getElementById('textInput');
        
        let input;
        if (this.state.currentTab === 'url' && urlInput) {
            input = urlInput.value.trim();
        } else if (textInput) {
            input = textInput.value.trim();
        }
            
        if (!input) {
            this.utils.showError('Please enter content to analyze');
            return;
        }

        this.state.isAnalyzing = true;
        this.utils.showLoading();

        try {
            const payload = this.state.currentTab === 'url' 
                ? { url: input, is_pro: CONFIG.isPro }
                : { text: input, is_pro: CONFIG.isPro };

            const response = await fetch(CONFIG.API_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const responseData = await response.json();
            
            if (!response.ok || !responseData.success) {
                throw new Error(responseData.error && responseData.error.message || 'Analysis failed');
            }

            const data = responseData.data;
            
            // Recalculate trust score
            const recalculatedScore = this.calculateTrustScore(data.detailed_analysis);
            if (recalculatedScore !== null) {
                data.analysis.trust_score = recalculatedScore;
                data.analysis.trust_level = this.utils.getTrustLevel(recalculatedScore);
            }

            this.state.currentAnalysis = data;
            this.state.currentMetadata = responseData.metadata || {};

            const self = this;
            setTimeout(function() {
                self.utils.hideLoading();
                if (self.display) {
                    self.display.showResults(data);
                }
            }, 1000);

        } catch (error) {
            console.error('Analysis error:', error);
            this.utils.hideLoading();
            this.utils.showError(error.message);
        } finally {
            this.state.isAnalyzing = false;
        }
    }

    calculateTrustScore(detailedAnalysis) {
        if (!detailedAnalysis) return null;

        let totalWeight = 0;
        let weightedScore = 0;
        const serviceScores = {};

        CONFIG.services.forEach(function(service) {
            if (service.id === 'content_analyzer' || service.id === 'plagiarism_detector') return;

            const serviceData = detailedAnalysis[service.id];
            if (!serviceData || Object.keys(serviceData).length === 0) return;

            const score = window.truthLensApp.extractServiceScore(service.id, serviceData);
            if (score !== null) {
                serviceScores[service.id] = score;
                weightedScore += score * service.weight;
                totalWeight += service.weight;
            }
        });

        if (Object.keys(serviceScores).length >= 2 && totalWeight > 0) {
            return Math.round(weightedScore / totalWeight);
        }

        return serviceScores.source_credibility ? Math.min(75, serviceScores.source_credibility) : null;
    }

    extractServiceScore(serviceId, data) {
        const extractors = {
            source_credibility: function(d) {
                return window.truthLensApp.utils.extractScore(d, ['credibility_score', 'score']);
            },
            author_analyzer: function(d) {
                const score = window.truthLensApp.utils.extractScore(d, ['author_score', 'score', 'credibility_score']);
                return score !== null ? score : (d.author_name ? 50 : null);
            },
            bias_detector: function(d) {
                const bias = window.truthLensApp.utils.extractScore(d, ['bias_score', 'score', 'overall_bias_score']);
                return bias !== null ? (100 - bias) : null;
            },
            fact_checker: function(d) {
                if (d.fact_checks && Array.isArray(d.fact_checks)) {
                    const total = d.fact_checks.length;
                    if (total === 0) return 100;
                    const verified = d.fact_checks.filter(function(c) {
                        return ['True', 'Verified', 'true'].indexOf(c.verdict) !== -1;
                    }).length;
                    return Math.round((verified / total) * 100);
                }
                return window.truthLensApp.utils.extractScore(d, ['accuracy_score', 'score']);
            },
            transparency_analyzer: function(d) {
                return window.truthLensApp.utils.extractScore(d, ['transparency_score', 'score']);
            },
            manipulation_detector: function(d) {
                const manipScore = window.truthLensApp.utils.extractScore(d, ['manipulation_score', 'score']);
                if (manipScore !== null) return 100 - manipScore;
                
                const levelScores = { 'Low': 90, 'Minimal': 95, 'Moderate': 50, 'High': 20, 'Extreme': 10 };
                return levelScores[d.manipulation_level] || null;
            }
        };

        const extractor = extractors[serviceId];
        return extractor ? extractor(data) : null;
    }

    toggleAccordion(serviceId) {
        const item = document.getElementById('service-' + serviceId);
        if (!item) return;

        const content = item.querySelector('.service-accordion-content');
        const icon = item.querySelector('.service-expand-icon');
        const wasActive = item.classList.contains('active');
        
        // Close all
        const allItems = document.querySelectorAll('.service-accordion-item');
        allItems.forEach(function(el) {
            el.classList.remove('active');
            const elContent = el.querySelector('.service-accordion-content');
            const elIcon = el.querySelector('.service-expand-icon');
            if (elContent) elContent.style.maxHeight = '0px';
            if (elIcon) elIcon.style.transform = 'rotate(0deg)';
        });
        
        // Open clicked if it wasn't active
        if (!wasActive) {
            item.classList.add('active');
            if (content) content.style.maxHeight = content.scrollHeight + 'px';
            if (icon) icon.style.transform = 'rotate(180deg)';
        }
    }

    async downloadPDF() {
        if (!this.state.currentAnalysis) {
            this.utils.showError('No analysis available to download');
            return;
        }
        
        this.utils.showLoading();
        
        try {
            const jsPDF = window.jspdf && window.jspdf.jsPDF;
            if (!jsPDF) {
                throw new Error('PDF library not loaded');
            }
            
            const doc = new jsPDF();
            
            if (this.services) {
                this.services.generatePDF(doc, this.state.currentAnalysis, this.state.currentMetadata);
            }
            
            doc.save('truthlens-analysis-' + Date.now() + '.pdf');
            
        } catch (error) {
            console.error('PDF generation error:', error);
            this.utils.showError('Failed to generate PDF report');
        } finally {
            this.utils.hideLoading();
        }
    }

    shareResults() {
        if (!this.state.currentAnalysis) {
            this.utils.showError('No analysis results to share');
            return;
        }

        const shareText = 'Check out this news analysis: Trust Score ' + 
                         this.state.currentAnalysis.analysis.trust_score + '/100';

        if (navigator.share) {
            navigator.share({
                title: 'TruthLens Analysis',
                text: shareText,
                url: window.location.href
            }).catch(function(err) {
                console.log('Error sharing:', err);
            });
        } else {
            const self = this;
            navigator.clipboard.writeText(window.location.href).then(function() {
                self.utils.showError('Link copied to clipboard!');
            });
        }
    }
}

// Utility functions
class TruthLensUtils {
    showError(message) {
        const errorEl = document.getElementById('errorMessage');
        if (!errorEl) return;
        
        const errorMap = {
            'timed out': 'Request timed out. The website may be blocking our service.',
            'timeout': 'Request timed out. Please try again.',
            '403': 'Access denied. This website blocks automated analysis.',
            '404': 'Article not found. Please check the URL.',
            '500': 'Server error. Please try again later.'
        };
        
        let displayMessage = message;
        for (const pattern in errorMap) {
            if (message.toLowerCase().indexOf(pattern) !== -1) {
                displayMessage = errorMap[pattern];
                break;
            }
        }
        
        errorEl.textContent = displayMessage;
        errorEl.classList.add('active');
        setTimeout(function() {
            window.truthLensApp.utils.hideError();
        }, 10000);
    }

    hideError() {
        const errorEl = document.getElementById('errorMessage');
        if (errorEl) {
            errorEl.classList.remove('active');
        }
    }

    showLoading() {
        const loadingEl = document.getElementById('loadingOverlay');
        if (loadingEl) {
            loadingEl.classList.add('active');
        }
    }

    hideLoading() {
        const loadingEl = document.getElementById('loadingOverlay');
        if (loadingEl) {
            loadingEl.classList.remove('active');
        }
    }

    extractScore(data, fields, defaultValue) {
        if (defaultValue === undefined) defaultValue = 0;
        if (!data || typeof data !== 'object') return defaultValue;
        
        for (let i = 0; i < fields.length; i++) {
            const field = fields[i];
            const value = parseFloat(data[field]);
            if (!isNaN(value)) return Math.round(value);
        }
        
        return defaultValue;
    }

    getScoreColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        return '#ef4444';
    }

    getTrustLevel(score) {
        if (score >= 80) return 'Very High';
        if (score >= 60) return 'High';
        if (score >= 40) return 'Moderate';
        if (score >= 20) return 'Low';
        return 'Very Low';
    }

    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        return new Date(dateString).toLocaleDateString('en-US', { 
            year: 'numeric', month: 'long', day: 'numeric' 
        });
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    window.truthLensApp = new TruthLensApp();
    
    // Re-initialize if other scripts load later
    setTimeout(function() {
        if (window.truthLensApp && !window.truthLensApp.display && typeof TruthLensDisplay !== 'undefined') {
            window.truthLensApp.display = new TruthLensDisplay(window.truthLensApp);
        }
        if (window.truthLensApp && !window.truthLensApp.services && typeof TruthLensServices !== 'undefined') {
            window.truthLensApp.services = new TruthLensServices(window.truthLensApp);
        }
    }, 100);
});
