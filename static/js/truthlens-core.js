// truthlens-core.js - Consolidated Core Application Logic
// Combines core functionality, state management, and API communication

// Global configuration
const CONFIG = {
    API_ENDPOINT: '/api/analyze',
    isPro: true,
    services: [
        { id: 'source_credibility', name: 'Source Credibility', icon: 'fa-shield-alt', weight: 0.25, isPro: false },
        { id: 'author_analyzer', name: 'Author Analysis', icon: 'fa-user-check', weight: 0.20, isPro: false },
        { id: 'bias_detector', name: 'Bias Detection', icon: 'fa-balance-scale', weight: 0.15, isPro: true },
        { id: 'fact_checker', name: 'Fact Verification', icon: 'fa-check-double', weight: 0.20, isPro: true },
        { id: 'transparency_analyzer', name: 'Transparency Analysis', icon: 'fa-eye', weight: 0.10, isPro: true },
        { id: 'manipulation_detector', name: 'Manipulation Detection', icon: 'fa-mask', weight: 0.10, isPro: true },
        { id: 'content_analyzer', name: 'Content Analysis', icon: 'fa-file-alt', weight: 0.05, isPro: true }
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
        this.display = new TruthLensDisplay(this);
        this.services = new TruthLensServices(this);
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        console.log('TruthLens initialized');
    }

    setupEventListeners() {
        // URL/Text input handlers
        document.getElementById('urlInput')?.addEventListener('keypress', e => {
            if (e.key === 'Enter') this.analyzeArticle();
        });
        
        document.getElementById('textInput')?.addEventListener('keypress', e => {
            if (e.key === 'Enter' && e.ctrlKey) this.analyzeArticle();
        });
        
        // Button handlers
        document.getElementById('analyzeBtn')?.addEventListener('click', () => this.analyzeArticle());
        document.getElementById('analyzeTextBtn')?.addEventListener('click', () => this.analyzeArticle());
        document.getElementById('resetBtn')?.addEventListener('click', () => this.resetAnalysis());
        document.getElementById('resetTextBtn')?.addEventListener('click', () => this.resetAnalysis());
        document.getElementById('downloadPdfBtn')?.addEventListener('click', () => this.downloadPDF());
        document.getElementById('shareResultsBtn')?.addEventListener('click', () => this.shareResults());
        
        // Tab switching
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', e => this.switchTab(e.currentTarget.getAttribute('data-mode')));
        });
        
        // Example buttons
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', e => {
                const url = e.target.getAttribute('data-url');
                if (url) {
                    document.getElementById('urlInput').value = url;
                    this.analyzeArticle();
                }
            });
        });
    }

    switchTab(mode) {
        this.state.currentTab = mode;
        
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-mode') === mode);
        });
        
        ['url', 'text'].forEach(type => {
            const isActive = type === mode;
            document.getElementById(`${type}Explanation`)?.classList.toggle('active', isActive);
            document.getElementById(`${type}InputWrapper`)?.classList.toggle('active', isActive);
        });
    }

    resetAnalysis() {
        document.getElementById('urlInput').value = '';
        document.getElementById('textInput').value = '';
        document.getElementById('resultsSection').style.display = 'none';
        this.state.currentAnalysis = null;
        this.state.currentMetadata = null;
    }

    async analyzeArticle() {
        if (this.state.isAnalyzing) return;

        const input = this.state.currentTab === 'url' 
            ? document.getElementById('urlInput')?.value?.trim()
            : document.getElementById('textInput')?.value?.trim();
            
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
                throw new Error(responseData.error?.message || 'Analysis failed');
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

            setTimeout(() => {
                this.utils.hideLoading();
                this.display.showResults(data);
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

        CONFIG.services.forEach(service => {
            if (service.id === 'content_analyzer') return;

            const serviceData = detailedAnalysis[service.id];
            if (!serviceData || Object.keys(serviceData).length === 0) return;

            const score = this.extractServiceScore(service.id, serviceData);
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
            source_credibility: d => this.utils.extractScore(d, ['credibility_score', 'score']),
            author_analyzer: d => {
                const score = this.utils.extractScore(d, ['author_score', 'score', 'credibility_score']);
                return score !== null ? score : (d.author_name ? 50 : null);
            },
            bias_detector: d => {
                const bias = this.utils.extractScore(d, ['bias_score', 'score', 'overall_bias_score']);
                return bias !== null ? (100 - bias) : null;
            },
            fact_checker: d => {
                if (d.fact_checks && Array.isArray(d.fact_checks)) {
                    const total = d.fact_checks.length;
                    if (total === 0) return 100;
                    const verified = d.fact_checks.filter(c => 
                        ['True', 'Verified', 'true'].includes(c.verdict)
                    ).length;
                    return Math.round((verified / total) * 100);
                }
                return this.utils.extractScore(d, ['accuracy_score', 'score']);
            },
            transparency_analyzer: d => this.utils.extractScore(d, ['transparency_score', 'score']),
            manipulation_detector: d => {
                const manipScore = this.utils.extractScore(d, ['manipulation_score', 'score']);
                if (manipScore !== null) return 100 - manipScore;
                
                const levelScores = { 'Low': 90, 'Minimal': 95, 'Moderate': 50, 'High': 20, 'Extreme': 10 };
                return levelScores[d.manipulation_level] || null;
            }
        };

        return extractors[serviceId]?.(data) || null;
    }

    toggleAccordion(serviceId) {
        const item = document.getElementById(`service-${serviceId}`);
        if (!item) return;

        const content = item.querySelector('.service-accordion-content');
        const icon = item.querySelector('.service-expand-icon');
        const wasActive = item.classList.contains('active');
        
        // Close all
        document.querySelectorAll('.service-accordion-item').forEach(el => {
            el.classList.remove('active');
            el.querySelector('.service-accordion-content').style.maxHeight = '0px';
            el.querySelector('.service-expand-icon')?.style.transform = 'rotate(0deg)';
        });
        
        // Open clicked if it wasn't active
        if (!wasActive) {
            item.classList.add('active');
            content.style.maxHeight = content.scrollHeight + 'px';
            icon?.style.transform = 'rotate(180deg)';
        }
    }

    async downloadPDF() {
        if (!this.state.currentAnalysis) {
            this.utils.showError('No analysis available to download');
            return;
        }
        
        this.utils.showLoading();
        
        try {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            
            this.services.generatePDF(doc, this.state.currentAnalysis, this.state.currentMetadata);
            doc.save(`truthlens-analysis-${Date.now()}.pdf`);
            
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

        const shareText = `Check out this news analysis: Trust Score ${this.state.currentAnalysis.analysis.trust_score}/100`;

        if (navigator.share) {
            navigator.share({
                title: 'TruthLens Analysis',
                text: shareText,
                url: window.location.href
            }).catch(err => console.log('Error sharing:', err));
        } else {
            navigator.clipboard.writeText(window.location.href).then(() => {
                this.utils.showError('Link copied to clipboard!');
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
        for (const [pattern, friendly] of Object.entries(errorMap)) {
            if (message.toLowerCase().includes(pattern)) {
                displayMessage = friendly;
                break;
            }
        }
        
        errorEl.textContent = displayMessage;
        errorEl.classList.add('active');
        setTimeout(() => this.hideError(), 10000);
    }

    hideError() {
        document.getElementById('errorMessage')?.classList.remove('active');
    }

    showLoading() {
        document.getElementById('loadingOverlay')?.classList.add('active');
    }

    hideLoading() {
        document.getElementById('loadingOverlay')?.classList.remove('active');
    }

    extractScore(data, fields, defaultValue = 0) {
        if (!data || typeof data !== 'object') return defaultValue;
        
        for (const field of fields) {
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
document.addEventListener('DOMContentLoaded', () => {
    window.truthLensApp = new TruthLensApp();
});
