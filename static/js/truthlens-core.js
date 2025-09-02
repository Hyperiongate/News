// CRITICAL FIX: truthlens-core.js - Data Structure Mismatch Resolved
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
                ? { url: input, is_pro: CONFIG.isPro || false }
                : { text: input, is_pro: CONFIG.isPro || false };

            console.log('=== Starting Analysis ===');
            console.log('Payload:', payload);

            const response = await fetch('/api/analyze', {
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
                hasTrustScore: typeof responseData.trust_score !== 'undefined',
                trustScore: responseData.trust_score,
                hasAuthor: typeof responseData.author !== 'undefined',
                author: responseData.author,
                hasSource: typeof responseData.source !== 'undefined',
                source: responseData.source,
                hasDetailedAnalysis: !!responseData.detailed_analysis,
                detailedAnalysisKeys: responseData.detailed_analysis ? Object.keys(responseData.detailed_analysis) : [],
                error: responseData.error
            });
            
            if (!response.ok || !responseData.success) {
                const errorMessage = responseData.error?.message || 
                                   responseData.message || 
                                   responseData.error ||
                                   'Analysis failed';
                throw new Error(errorMessage);
            }

            // CRITICAL FIX: The root cause of your week-long problem!
            // Your backend returns data at root level, not wrapped in 'data' field
            // OLD (BROKEN): this.handleAnalysisComplete(responseData.data);
            // NEW (FIXED): Pass responseData directly
            console.log('=== CRITICAL FIX APPLIED ===');
            console.log('Calling handleAnalysisComplete with responseData directly (not responseData.data)');
            this.handleAnalysisComplete(responseData);

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
        console.log('=== Analysis Complete Handler - FIXED VERSION ===');
        console.log('Data structure validation:', {
            isObject: typeof data === 'object',
            hasSuccessField: 'success' in data,
            hasTrustScore: 'trust_score' in data,
            hasAuthor: 'author' in data,
            hasSource: 'source' in data,
            hasArticleSummary: 'article_summary' in data,
            hasFindingsSummary: 'findings_summary' in data,
            hasDetailedAnalysis: 'detailed_analysis' in data
        });
        
        // EXTENSIVE VALIDATION AND LOGGING
        if (!data || typeof data !== 'object') {
            console.error('CRITICAL: Invalid data structure received');
            throw new Error('Invalid analysis data received');
        }

        // Log the actual values we received
        console.log('=== RECEIVED DATA VALUES ===');
        console.log('Trust Score:', data.trust_score);
        console.log('Article Summary:', data.article_summary ? data.article_summary.substring(0, 50) + '...' : 'None');
        console.log('Source:', data.source);
        console.log('Author:', data.author);
        console.log('Findings Summary:', data.findings_summary ? data.findings_summary.substring(0, 50) + '...' : 'None');
        console.log('Detailed Analysis Services:', data.detailed_analysis ? Object.keys(data.detailed_analysis).length : 0);
        
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
                console.log('=== Calling display.showResults with fixed data ===');
                this.display.showResults(data);
            } else {
                console.log('Display object not available, showing results directly');
                this.showResultsDirect(data);
            }
            this.state.isAnalyzing = false;
        }, 1000);
    }

    // Fallback method if display object not available
    showResultsDirect(data) {
        console.log('=== Showing results directly ===');
        
        // Show results section
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.classList.add('show');
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        
        // Update trust score
        this.updateTrustScore(data.trust_score || 0);
        
        // Update overview content
        const overviewEl = document.getElementById('analysisOverview');
        if (overviewEl) {
            overviewEl.classList.remove('trust-high', 'trust-medium', 'trust-low');
            const trustScore = data.trust_score || 0;
            if (trustScore >= 70) {
                overviewEl.classList.add('trust-high');
            } else if (trustScore >= 40) {
                overviewEl.classList.add('trust-medium');
            } else {
                overviewEl.classList.add('trust-low');
            }
        }
        
        // Update text content
        const articleSummary = data.article_summary || 'Article summary not available';
        const source = data.source || 'Unknown';
        const author = data.author || 'Unknown';
        const findingsSummary = data.findings_summary || 'Analysis completed.';
        
        this.updateElementText('articleSummary', 
            articleSummary.length > 100 ? articleSummary.substring(0, 100) + '...' : articleSummary
        );
        this.updateElementText('articleSource', source);
        this.updateElementText('articleAuthor', author);
        this.updateElementText('findingsSummary', findingsSummary);
        
        console.log('Results displayed successfully');
    }

    updateElementText(id, text) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = text;
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
            const trustScore = this.state.currentAnalysis.trust_score;
            const source = this.state.currentAnalysis.source;
            
            const shareData = {
                title: source && source !== 'Unknown' ? `News Analysis: ${source}` : 'News Analysis',
                text: trustScore !== undefined && trustScore !== null
                    ? `Trust Score: ${trustScore}/100` 
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
        if (!errorEl || !errorTextEl) {
            console.error('Error elements not found in DOM');
            alert('Error: ' + message); // Fallback
            return;
        }
        
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
    // Set up CONFIG if it doesn't exist
    if (typeof CONFIG === 'undefined') {
        window.CONFIG = {
            API_ENDPOINT: '/api/analyze',
            isPro: false
        };
    }
    
    window.truthLensApp = new TruthLensApp();
    console.log('TruthLens App initialized with CRITICAL FIX applied');
});
