// truthlens-core.js - Complete File with Real-time Updates
// Main Application Logic with Enhanced Progress Tracking

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
        
        // Real-time update properties
        this.analysisSSE = null;
        this.pollingInterval = null;
        this.analysisId = null;
        
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
        console.log('TruthLens initialized with real-time updates');
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
        
        // Clear any polling
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
        
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
        this.analysisId = null;
        
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

            console.log('Response parsed:', {
                success: responseData.success,
                hasData: !!responseData.data,
                hasAnalysisId: !!responseData.analysis_id,
                error: responseData.error
            });
            
            if (!response.ok || !responseData.success) {
                const errorMessage = responseData.error?.message || 
                                   responseData.message || 
                                   'Analysis failed';
                throw new Error(errorMessage);
            }

            // Check if we got an analysis ID for polling
            if (responseData.analysis_id) {
                // Start polling for updates
                this.analysisId = responseData.analysis_id;
                this.startProgressPolling();
            } else {
                // Legacy mode - we got all data at once
                this.handleAnalysisComplete(responseData.data);
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
    }

    // Start polling for analysis progress
    startProgressPolling() {
        console.log('Starting progress polling for analysis:', this.analysisId);
        
        let pollCount = 0;
        const maxPolls = 60; // 5 minutes maximum
        
        this.pollingInterval = setInterval(async () => {
            pollCount++;
            
            try {
                const response = await fetch(`/api/analyze/status/${this.analysisId}`);
                const data = await response.json();
                
                console.log('Progress update:', data);
                
                if (data.status === 'complete') {
                    // Analysis complete
                    clearInterval(this.pollingInterval);
                    this.pollingInterval = null;
                    this.handleAnalysisComplete(data.data);
                    
                } else if (data.status === 'failed') {
                    // Analysis failed
                    clearInterval(this.pollingInterval);
                    this.pollingInterval = null;
                    throw new Error(data.error || 'Analysis failed');
                    
                } else if (data.status === 'processing') {
                    // Update progress
                    this.updateAnalysisProgress(data);
                }
                
                // Timeout check
                if (pollCount >= maxPolls) {
                    clearInterval(this.pollingInterval);
                    this.pollingInterval = null;
                    throw new Error('Analysis timed out - please try again');
                }
                
            } catch (error) {
                console.error('Polling error:', error);
                clearInterval(this.pollingInterval);
                this.pollingInterval = null;
                this.utils.hideLoading();
                this.utils.showError(error.message);
                this.state.isAnalyzing = false;
            }
        }, 5000); // Poll every 5 seconds
    }

    // Update analysis progress in real-time
    updateAnalysisProgress(progressData) {
        const {
            services_completed = 0,
            services_total = 10,
            current_service = '',
            partial_results = {}
        } = progressData;

        const percentage = Math.round((services_completed / services_total) * 100);
        
        // Update loading steps based on progress
        this.updateLoadingSteps(services_completed);
        
        // If we have partial results, update the UI incrementally
        if (partial_results && Object.keys(partial_results).length > 0) {
            this.updatePartialResults(partial_results);
        }
    }

    // Update loading steps
    updateLoadingSteps(completedCount) {
        const steps = [
            { id: 'step1', threshold: 1, icon: 'fa-check-circle' },
            { id: 'step2', threshold: 3, icon: 'fa-spinner fa-spin' },
            { id: 'step3', threshold: 6, icon: 'fa-circle' },
            { id: 'step4', threshold: 9, icon: 'fa-circle' }
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

    // Update UI with partial results
    updatePartialResults(partialData) {
        // Show results section if hidden
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection && resultsSection.style.display === 'none') {
            resultsSection.style.display = 'block';
            resultsSection.classList.add('active');
        }
        
        // Update trust score if available
        if (partialData.trust_score !== undefined) {
            const scoreEl = document.getElementById('trustScoreNumber');
            if (scoreEl) {
                scoreEl.textContent = partialData.trust_score;
            }
        }
        
        // Update service cards incrementally
        if (partialData.services) {
            this.updateServiceCards(partialData.services);
        }
    }

    // Update service cards with real-time data
    updateServiceCards(servicesData) {
        Object.entries(servicesData).forEach(([serviceId, serviceData]) => {
            const card = document.querySelector(`.service-card.${serviceId.replace(/_/g, '-')}`);
            if (card && serviceData) {
                // Remove pending class
                card.classList.remove('pending');
                card.classList.add('complete');
                
                // Update status
                const statusEl = card.querySelector('.service-status');
                if (statusEl) {
                    statusEl.innerHTML = '<i class="fas fa-check-circle"></i> Complete';
                    statusEl.classList.add('complete');
                }
                
                // Update preview if needed
                const previewEl = card.querySelector('.service-preview');
                if (previewEl && this.display) {
                    previewEl.textContent = this.display.getServicePreview(serviceId, serviceData);
                }
                
                // Make card clickable
                card.style.cursor = 'pointer';
                card.onclick = null;
            }
        });
    }

    // Handle complete analysis
    handleAnalysisComplete(data) {
        console.log('=== Analysis Complete ===');
        console.log('Data structure:', {
            hasArticle: !!data.article,
            hasAnalysis: !!data.analysis,
            hasDetailedAnalysis: !!data.detailed_analysis,
            detailedServices: data.detailed_analysis ? Object.keys(data.detailed_analysis) : []
        });
        
        // Clear polling
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
        
        // Validate data
        if (!data || typeof data !== 'object') {
            throw new Error('Invalid analysis data received');
        }
        
        // Store the complete analysis
        this.state.currentAnalysis = data;
        this.state.currentMetadata = data.metadata || {};
        
        // Save to storage for service pages
        if (window.ServiceNavigation) {
            window.ServiceNavigation.saveAnalysisData(data, window.location.href);
        }
        
        // Trigger custom event
        window.dispatchEvent(new CustomEvent('analysisComplete', { detail: data }));
        
        // Update all loading steps to complete
        this.updateLoadingSteps(10);
        
        // Hide loading and show results
        setTimeout(() => {
            this.utils.hideLoading();
            if (this.display) {
                this.display.showResults(data);
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
