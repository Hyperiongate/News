// truthlens-core.js - Complete File with FIXED Data Flow
// Main Application Logic - COMPLETELY REPAIRED

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
            urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.analyzeArticle();
                }
            });
        }
        
        const textInput = document.getElementById('textInput');
        if (textInput) {
            textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.analyzeArticle();
                }
            });
            
            // Word count update
            textInput.addEventListener('input', (e) => {
                const wordCount = e.target.value.trim().split(/\s+/).filter(word => word.length > 0).length;
                const wordCountEl = document.getElementById('wordCount');
                if (wordCountEl) {
                    wordCountEl.textContent = `${wordCount} words`;
                }
            });
        }
        
        // Button handlers
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => {
                this.analyzeArticle();
            });
        }
        
        const analyzeTextBtn = document.getElementById('analyzeTextBtn');
        if (analyzeTextBtn) {
            analyzeTextBtn.addEventListener('click', () => {
                this.analyzeArticle();
            });
        }
        
        const downloadPdfBtn = document.getElementById('downloadPdfBtn');
        if (downloadPdfBtn) {
            downloadPdfBtn.addEventListener('click', () => {
                this.downloadPDF();
            });
        }
        
        const shareResultsBtn = document.getElementById('shareResultsBtn');
        if (shareResultsBtn) {
            shareResultsBtn.addEventListener('click', () => {
                this.shareResults();
            });
        }
        
        const newAnalysisBtn = document.getElementById('newAnalysisBtn');
        if (newAnalysisBtn) {
            newAnalysisBtn.addEventListener('click', () => {
                this.resetAnalysis();
            });
        }
        
        // Tab switching
        const modeBtns = document.querySelectorAll('.mode-tab');
        modeBtns.forEach((btn) => {
            btn.addEventListener('click', (e) => {
                const mode = e.currentTarget.getAttribute('data-mode');
                this.switchTab(mode);
            });
        });
        
        // Example buttons
        const exampleBtns = document.querySelectorAll('.example-chip');
        exampleBtns.forEach((btn) => {
            btn.addEventListener('click', (e) => {
                const url = e.target.getAttribute('data-url');
                if (url) {
                    const urlInput = document.getElementById('urlInput');
                    if (urlInput) {
                        urlInput.value = url;
                        this.analyzeArticle();
                    }
                }
            });
        });
    }

    switchTab(mode) {
        this.state.currentTab = mode;
        
        const modeBtns = document.querySelectorAll('.mode-tab');
        modeBtns.forEach((btn) => {
            if (btn.getAttribute('data-mode') === mode) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // Update input panels
        const panels = document.querySelectorAll('.input-panel');
        panels.forEach(panel => {
            panel.classList.remove('active');
        });
        
        if (mode === 'url') {
            document.getElementById('urlInputWrapper')?.classList.add('active');
        } else {
            document.getElementById('textInputWrapper')?.classList.add('active');
        }
    }

    resetAnalysis() {
        // Clear inputs
        const urlInput = document.getElementById('urlInput');
        const textInput = document.getElementById('textInput');
        const resultsSection = document.getElementById('resultsSection');
        
        if (urlInput) urlInput.value = '';
        if (textInput) textInput.value = '';
        if (resultsSection) {
            resultsSection.style.display = 'none';
            resultsSection.classList.remove('active');
        }
        
        // Clear word count
        const wordCountEl = document.getElementById('wordCount');
        if (wordCountEl) wordCountEl.textContent = '0 words';
        
        // Destroy any existing charts
        if (this.state.charts) {
            Object.values(this.state.charts).forEach(chart => {
                if (chart && typeof chart.destroy === 'function') {
                    chart.destroy();
                }
            });
        }
        
        // Reset state
        this.state.currentAnalysis = null;
        this.state.currentMetadata = null;
        this.state.charts = {};
        
        // Clear stored data
        if (window.ServiceNavigation) {
            window.ServiceNavigation.clearAnalysisData();
        }
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
        } else {
            // Validate text length
            const wordCount = input.split(/\s+/).filter(word => word.length > 0).length;
            if (wordCount < 100) {
                this.utils.showError('Please enter at least 100 words for accurate analysis');
                return;
            }
        }

        this.state.isAnalyzing = true;
        this.showEnhancedLoading();

        try {
            const payload = this.state.currentTab === 'url' 
                ? { url: input, is_pro: CONFIG.isPro }
                : { text: input, is_pro: CONFIG.isPro };

            console.log('=== Starting Analysis ===');
            console.log('Payload:', payload);

            const response = await fetch(CONFIG.API_ENDPOINT, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const responseText = await response.text();
            console.log('Response received, length:', responseText.length);

            let responseData;
            try {
                responseData = JSON.parse(responseText);
            } catch (e) {
                console.error('Failed to parse response:', e);
                throw new Error('Invalid response format from server');
            }

            console.log('=== CRITICAL DEBUG: Response Analysis ===');
            console.log('Response structure:', {
                success: responseData.success,
                hasData: !!responseData.data,
                dataKeys: responseData.data ? Object.keys(responseData.data) : [],
                hasDetailedAnalysis: !!(responseData.data && responseData.data.detailed_analysis),
                detailedAnalysisKeys: responseData.data?.detailed_analysis ? Object.keys(responseData.data.detailed_analysis) : [],
                error: responseData.error
            });
            
            if (!response.ok || !responseData.success) {
                const errorMessage = responseData.error?.message || 
                                   responseData.message || 
                                   responseData.error ||
                                   'Analysis failed';
                throw new Error(errorMessage);
            }

            // CRITICAL FIX: Handle immediate complete results
            // Your backend returns complete data immediately, not analysis_id
            if (responseData.data) {
                console.log('=== IMMEDIATE COMPLETE RESULTS DETECTED ===');
                this.handleAnalysisComplete(responseData.data);
            } else {
                throw new Error('No analysis data received from server');
            }

        } catch (error) {
            console.error('Analysis Error:', error);
            this.utils.hideLoading();
            
            let errorMessage = error.message;
            if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Unable to connect to the analysis server. Please try again.';
            }
            
            this.utils.showError(errorMessage);
            this.state.isAnalyzing = false;
        }
    }

    // Show enhanced loading with progress
    showEnhancedLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (!overlay) {
            this.utils.showLoading();
            return;
        }
        
        overlay.classList.add('active');
        
        // Reset loading steps
        const steps = ['step1', 'step2', 'step3', 'step4'];
        steps.forEach(stepId => {
            const stepEl = document.getElementById(stepId);
            if (stepEl) {
                stepEl.classList.remove('active');
                stepEl.querySelector('i').className = 'fas fa-circle';
            }
        });
        
        // Activate first step
        const step1 = document.getElementById('step1');
        if (step1) {
            step1.classList.add('active');
            step1.querySelector('i').className = 'fas fa-spinner fa-spin';
        }
        
        // Simulate progress for better UX
        setTimeout(() => this.updateLoadingSteps(1), 500);
        setTimeout(() => this.updateLoadingSteps(2), 1000);
        setTimeout(() => this.updateLoadingSteps(3), 1500);
    }

    // Update loading steps
    updateLoadingSteps(completedCount) {
        const steps = [
            { id: 'step1', threshold: 1, icon: 'fa-check-circle' },
            { id: 'step2', threshold: 2, icon: 'fa-spinner fa-spin' },
            { id: 'step3', threshold: 3, icon: 'fa-circle' },
            { id: 'step4', threshold: 4, icon: 'fa-circle' }
        ];
        
        steps.forEach((step, index) => {
            const stepEl = document.getElementById(step.id);
            if (!stepEl) return;
            
            if (completedCount >= step.threshold) {
                stepEl.classList.add('active');
                if (index < steps.length - 1 && completedCount < steps[index + 1].threshold) {
                    // This is the current step
                    stepEl.querySelector('i').className = 'fas fa-spinner fa-spin';
                } else {
                    // This step is complete
                    stepEl.querySelector('i').className = 'fas fa-check-circle';
                }
            }
        });
    }

    // CRITICAL FIX: Handle complete analysis - COMPLETELY REPAIRED
    handleAnalysisComplete(data) {
        console.log('=== Analysis Complete Handler ===');
        console.log('Data received:', {
            hasArticle: !!data.article,
            hasAnalysis: !!data.analysis,
            hasDetailedAnalysis: !!data.detailed_analysis,
            detailedServicesCount: data.detailed_analysis ? Object.keys(data.detailed_analysis).length : 0,
            detailedServices: data.detailed_analysis ? Object.keys(data.detailed_analysis) : []
        });
        
        // EXTENSIVE VALIDATION AND LOGGING
        if (!data || typeof data !== 'object') {
            console.error('CRITICAL: Invalid data structure received');
            throw new Error('Invalid analysis data received');
        }

        if (!data.detailed_analysis || Object.keys(data.detailed_analysis).length === 0) {
            console.warn('WARNING: No detailed_analysis data found');
            console.log('Available data keys:', Object.keys(data));
            // Continue anyway - some data is better than none
        }

        // Log each service's data for debugging
        if (data.detailed_analysis) {
            Object.entries(data.detailed_analysis).forEach(([serviceName, serviceData]) => {
                console.log(`Service ${serviceName}:`, {
                    hasData: !!serviceData,
                    dataType: typeof serviceData,
                    keys: Object.keys(serviceData || {}),
                    score: serviceData?.score,
                    level: serviceData?.level
                });
            });
        }
        
        // Store the complete analysis
        this.state.currentAnalysis = data;
        this.state.currentMetadata = data.metadata || {};
        
        // Save to storage for service pages
        if (window.ServiceNavigation) {
            window.ServiceNavigation.saveAnalysisData(data, window.location.href);
        } else {
            // Fallback to sessionStorage
            try {
                sessionStorage.setItem('analysisData', JSON.stringify(data));
                console.log('Saved analysis data to sessionStorage');
            } catch (e) {
                console.warn('Failed to save to sessionStorage:', e);
            }
        }
        
        // Trigger custom event
        window.dispatchEvent(new CustomEvent('analysisComplete', { detail: data }));
        
        // Update loading to complete
        this.updateLoadingSteps(4);
        
        // Hide loading and show results
        setTimeout(() => {
            this.utils.hideLoading();
            if (this.display) {
                console.log('=== Calling display.showResults ===');
                this.display.showResults(data);
            } else {
                console.error('CRITICAL: Display object not available');
            }
            this.state.isAnalyzing = false;
        }, 1000);
    }

    downloadPDF() {
        if (!this.state.currentAnalysis) {
            this.utils.showError('No analysis available to download. Please analyze an article first.');
            return;
        }
        
        // TODO: Implement PDF download functionality
        console.log('Download PDF clicked');
        console.log('Analysis data available:', this.state.currentAnalysis);
        this.utils.showError('PDF download feature coming soon!');
    }

    shareResults() {
        if (!this.state.currentAnalysis) {
            this.utils.showError('No analysis results to share. Please analyze an article first.');
            return;
        }
        
        console.log('Share results clicked');
        
        if (!navigator.share) {
            this.utils.showError('Sharing is not supported on this device or browser. You can copy the URL to share.');
            return;
        }
        
        try {
            const article = this.state.currentAnalysis.article || {};
            const analysis = this.state.currentAnalysis.analysis || {};
            
            const shareData = {
                title: article.title ? `News Analysis: ${article.title}` : 'News Analysis',
                text: analysis.trust_score !== undefined && analysis.trust_score !== null
                    ? `Trust Score: ${analysis.trust_score}/100` 
                    : 'Check out this news analysis',
                url: window.location.href
            };
            
            navigator.share(shareData)
                .then(() => {
                    console.log('Successfully shared');
                })
                .catch(err => {
                    console.log('Share failed:', err);
                    if (err.name !== 'AbortError') {
                        this.utils.showError('Failed to share results. Please try again.');
                    }
                });
        } catch (error) {
            console.error('Error preparing share data:', error);
            this.utils.showError('Failed to prepare share data. Please try again.');
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
        setTimeout(() => {
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

    extractScore(data, fields, defaultValue = 0) {
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
            if (isNaN(date.getTime())) {
                return dateString;
            }
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
        
        const number = parseFloat(num);
        if (isNaN(number)) return '0';
        
        if (number >= 1000000) {
            return (number / 1000000).toFixed(1) + 'M';
        } else if (number >= 1000) {
            return (number / 1000).toFixed(1) + 'K';
        }
        return number.toString();
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.truthLensApp = new TruthLensApp();
    console.log('TruthLens App initialized');
});
