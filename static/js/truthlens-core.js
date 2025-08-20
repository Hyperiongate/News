// truthlens-core.js - Main Application Logic
// Uses shared CONFIG from config.js

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
        this.display = null;
        this.services = null;
        
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
        
        const newAnalysisBtn = document.getElementById('newAnalysisBtn');
        if (newAnalysisBtn) {
            newAnalysisBtn.addEventListener('click', function() {
                window.truthLensApp.resetAnalysis();
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
        
        // Hide all explanations and inputs first
        document.getElementById('urlExplanation').style.display = 'none';
        document.getElementById('textExplanation').style.display = 'none';
        document.getElementById('urlInputWrapper').style.display = 'none';
        document.getElementById('textInputWrapper').style.display = 'none';
        
        // Show the active mode
        if (mode === 'url') {
            document.getElementById('urlExplanation').style.display = 'block';
            document.getElementById('urlInputWrapper').style.display = 'block';
        } else {
            document.getElementById('textExplanation').style.display = 'block';
            document.getElementById('textInputWrapper').style.display = 'block';
        }
    }

    resetAnalysis() {
        const urlInput = document.getElementById('urlInput');
        const textInput = document.getElementById('textInput');
        const resultsSection = document.getElementById('resultsSection');
        
        if (urlInput) urlInput.value = '';
        if (textInput) textInput.value = '';
        if (resultsSection) {
            resultsSection.style.display = 'none';
            resultsSection.classList.remove('active');
        }
        
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

        // Validate URL if in URL mode
        if (this.state.currentTab === 'url') {
            try {
                new URL(input);
            } catch (e) {
                this.utils.showError('Please enter a valid URL starting with http:// or https://');
                return;
            }
        }

        this.state.isAnalyzing = true;
        this.utils.showLoading();

        try {
            const payload = this.state.currentTab === 'url' 
                ? { url: input, is_pro: CONFIG.isPro }
                : { text: input, is_pro: CONFIG.isPro };

            console.log('=== API Request Debug ===');
            console.log('Sending payload:', JSON.stringify(payload, null, 2));

            const response = await fetch(CONFIG.API_ENDPOINT, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const responseText = await response.text();
            console.log('Raw response:', responseText);

            let responseData;
            try {
                responseData = JSON.parse(responseText);
            } catch (e) {
                console.error('Failed to parse response:', e);
                throw new Error('Invalid response format from server');
            }

            console.log('Parsed response structure:', {
                success: responseData.success,
                hasData: !!responseData.data,
                dataKeys: responseData.data ? Object.keys(responseData.data) : [],
                hasDetailedAnalysis: !!(responseData.data && responseData.data.detailed_analysis),
                detailedAnalysisKeys: responseData.data && responseData.data.detailed_analysis ? 
                    Object.keys(responseData.data.detailed_analysis) : []
            });
            
            if (!response.ok || !responseData.success) {
                throw new Error(responseData.error && responseData.error.message || 'Analysis failed');
            }

            // Store the entire response data structure
            const data = responseData.data;
            
            // Store the complete analysis
            this.state.currentAnalysis = data;
            this.state.currentMetadata = responseData.metadata || {};

            // Log what we're storing
            console.log('=== Stored Analysis ===');
            console.log('Article:', data.article ? Object.keys(data.article) : 'missing');
            console.log('Analysis:', data.analysis ? Object.keys(data.analysis) : 'missing');
            console.log('Detailed Analysis Services:', data.detailed_analysis ? 
                Object.keys(data.detailed_analysis) : 'missing');

            const self = this;
            setTimeout(function() {
                self.utils.hideLoading();
                if (self.display) {
                    // Pass the complete data structure
                    self.display.showResults(data);
                }
            }, 1000);

        } catch (error) {
            console.error('Analysis Error:', error);
            this.utils.hideLoading();
            
            let errorMessage = error.message;
            if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Unable to connect to the analysis server. Please try again.';
            }
            
            this.utils.showError(errorMessage);
        } finally {
            this.state.isAnalyzing = false;
        }
    }

    toggleAccordion(serviceId) {
        const item = document.getElementById('service-' + serviceId);
        if (item) {
            item.classList.toggle('active');
        }
    }

    downloadPDF() {
        // Implement PDF download
        console.log('Download PDF clicked');
        this.utils.showError('PDF download coming soon!');
    }

    shareResults() {
        // Implement share functionality
        console.log('Share results clicked');
        if (navigator.share && this.state.currentAnalysis) {
            const article = this.state.currentAnalysis.article;
            navigator.share({
                title: 'News Analysis: ' + (article.title || 'Article'),
                text: 'Trust Score: ' + this.state.currentAnalysis.analysis.trust_score + '/100',
                url: window.location.href
            }).catch(err => console.log('Share failed:', err));
        } else {
            this.utils.showError('Sharing not supported on this device');
        }
    }
}

// Utility functions
class TruthLensUtils {
    showError(message) {
        const errorEl = document.getElementById('errorMessage');
        const errorTextEl = document.getElementById('errorText');
        if (!errorEl || !errorTextEl) return;
        
        const errorMap = {
            'timed out': 'Request timed out. The website may be blocking our service.',
            'timeout': 'Request timed out. Please try again.',
            '403': 'Access denied. This website blocks automated analysis.',
            '404': 'Article not found. Please check the URL.',
            '500': 'Server error. Please try again later.',
            'extraction methods failed': 'Unable to extract article content. Try using Text Mode instead.',
            'Invalid URL': 'Please enter a valid news article URL starting with http:// or https://',
            'No domain': 'Could not determine the source domain from the URL.'
        };
        
        let displayMessage = message;
        for (const pattern in errorMap) {
            if (message.toLowerCase().indexOf(pattern.toLowerCase()) !== -1) {
                displayMessage = errorMap[pattern];
                break;
            }
        }
        
        errorTextEl.textContent = displayMessage;
        errorEl.classList.add('active');
        setTimeout(function() {
            errorEl.classList.remove('active');
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
        
        for (const field of fields) {
            if (data && data[field] !== undefined && data[field] !== null) {
                return data[field];
            }
        }
        return defaultValue;
    }

    getScoreColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        if (score >= 20) return '#ef4444';
        return '#991b1b';
    }

    formatDate(dateString) {
        if (!dateString) return '';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (e) {
            return dateString;
        }
    }

    formatNumber(num) {
        if (num === null || num === undefined) return '0';
        
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.truthLensApp = new TruthLensApp();
});
