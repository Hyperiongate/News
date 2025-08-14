// truthlens-core.js - Core Application Logic and API Communication
// This file contains the main TruthLensApp class with core functionality

// ============================================================================
// SECTION 1: Configuration and Constants
// ============================================================================

// Global state
let currentAnalysis = null;
let isAnalyzing = false;
let charts = {};
let isPro = true; // For development, keep pro features open

// Service definitions
const services = [
    {
        id: 'source_credibility',
        name: 'Source Credibility',
        icon: 'fa-shield-alt',
        description: 'Evaluates the reliability and trustworthiness of the news source',
        isPro: false
    },
    {
        id: 'author_analyzer',
        name: 'Author Analysis',
        icon: 'fa-user-check',
        description: 'Analyzes author credentials and publishing history',
        isPro: false
    },
    {
        id: 'bias_detector',
        name: 'Bias Detection',
        icon: 'fa-balance-scale',
        description: 'Identifies political, ideological, and narrative biases',
        isPro: true
    },
    {
        id: 'fact_checker',
        name: 'Fact Verification',
        icon: 'fa-check-double',
        description: 'Verifies claims against trusted fact-checking databases',
        isPro: true
    },
    {
        id: 'transparency_analyzer',
        name: 'Transparency Analysis',
        icon: 'fa-eye',
        description: 'Evaluates source disclosure and funding transparency',
        isPro: true
    },
    {
        id: 'manipulation_detector',
        name: 'Manipulation Detection',
        icon: 'fa-mask',
        description: 'Detects emotional manipulation and propaganda techniques',
        isPro: true
    },
    {
        id: 'content_analyzer',
        name: 'Content Analysis',
        icon: 'fa-file-alt',
        description: 'Analyzes writing quality, structure, and coherence',
        isPro: true
    }
];

// ============================================================================
// SECTION 2: TruthLensApp Core Class
// ============================================================================

class TruthLensApp {
    constructor() {
        this.currentAnalysis = null;
        this.currentMetadata = null;
        this.isPremium = false;
        this.currentTab = 'url';
        this.API_ENDPOINT = '/api/analyze';
        this.progressInterval = null;
        this.analysisStartTime = null;
        
        // Check if components are available
        if (typeof AnalysisComponents !== 'undefined') {
            this.analysisComponents = new AnalysisComponents();
        }
        
        // Check if display methods are available
        if (typeof TruthLensDisplay !== 'undefined') {
            Object.assign(this, TruthLensDisplay);
        }
        
        // Check if service methods are available
        if (typeof TruthLensServices !== 'undefined') {
            Object.assign(this, TruthLensServices);
        }
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupTabSwitching();
        this.loadSampleData();
        console.log('TruthLens initialized');
    }

    setupEventListeners() {
        // URL input
        const urlInput = document.getElementById('urlInput');
        if (urlInput) {
            urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.analyzeArticle();
                }
            });
        }

        // Text input
        const textInput = document.getElementById('textInput');
        if (textInput) {
            textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.analyzeArticle();
                }
            });
        }

        // Analyze buttons
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeArticle());
        }

        const analyzeTextBtn = document.getElementById('analyzeTextBtn');
        if (analyzeTextBtn) {
            analyzeTextBtn.addEventListener('click', () => this.analyzeArticle());
        }

        // Reset buttons
        const resetBtn = document.getElementById('resetBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetAnalysis());
        }

        const resetTextBtn = document.getElementById('resetTextBtn');
        if (resetTextBtn) {
            resetTextBtn.addEventListener('click', () => this.resetAnalysis());
        }

        // Download PDF button
        const downloadBtn = document.getElementById('downloadPdfBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadPDF());
        }

        // Share button
        const shareBtn = document.getElementById('shareResultsBtn');
        if (shareBtn) {
            shareBtn.addEventListener('click', () => this.shareResults());
        }

        // Example buttons for site blocking message
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const url = e.target.getAttribute('data-url');
                if (url && urlInput) {
                    urlInput.value = url;
                    this.analyzeArticle();
                }
            });
        });
    }

    setupTabSwitching() {
        const modeBtns = document.querySelectorAll('.mode-btn');
        modeBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mode = e.currentTarget.getAttribute('data-mode');
                this.switchTab(mode);
            });
        });
    }

    switchTab(mode) {
        this.currentTab = mode;
        
        // Update button states
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-mode') === mode);
        });
        
        // Update explanation texts
        document.getElementById('urlExplanation').classList.toggle('active', mode === 'url');
        document.getElementById('textExplanation').classList.toggle('active', mode === 'text');
        
        // Update input wrappers
        document.getElementById('urlInputWrapper').classList.toggle('active', mode === 'url');
        document.getElementById('textInputWrapper').classList.toggle('active', mode === 'text');
    }

    resetAnalysis() {
        // Clear inputs
        const urlInput = document.getElementById('urlInput');
        const textInput = document.getElementById('textInput');
        if (urlInput) urlInput.value = '';
        if (textInput) textInput.value = '';
        
        // Hide results
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
        
        // Clear current analysis and metadata
        this.currentAnalysis = null;
        this.currentMetadata = null;
        currentAnalysis = null;
        window.currentAnalysis = null;
    }

    async analyzeArticle() {
        if (isAnalyzing) return;

        const urlInput = document.getElementById('urlInput');
        const textInput = document.getElementById('textInput');
        
        let input;
        let inputType;

        if (this.currentTab === 'url') {
            input = urlInput?.value?.trim();
            inputType = 'url';
            if (!input) {
                this.showError('Please enter a URL to analyze');
                return;
            }
        } else {
            input = textInput?.value?.trim();
            inputType = 'text';
            if (!input) {
                this.showError('Please enter text to analyze');
                return;
            }
        }

        isAnalyzing = true;
        this.analysisStartTime = Date.now();
        this.showLoading();
        this.resetProgress();
        this.startProgressAnimation();

        try {
            const payload = inputType === 'url' ? { url: input } : { text: input };
            payload.is_pro = isPro;

            const response = await fetch(this.API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const responseData = await response.json();
            
            // DETAILED DEBUG LOGGING
            console.log('=== FULL API RESPONSE ===');
            console.log('Response status:', response.status);
            console.log('Response OK:', response.ok);
            console.log('Full responseData:', JSON.stringify(responseData, null, 2));
            
            if (responseData.data) {
                console.log('=== DATA OBJECT ===');
                console.log('data keys:', Object.keys(responseData.data));
                console.log('data.article:', responseData.data.article);
                console.log('data.analysis:', responseData.data.analysis);
                console.log('data.detailed_analysis keys:', responseData.data.detailed_analysis ? Object.keys(responseData.data.detailed_analysis) : 'undefined');
            }
            
            if (responseData.metadata) {
                console.log('=== METADATA ===');
                console.log('metadata:', responseData.metadata);
            }

            if (!response.ok || !responseData.success) {
                throw new Error(responseData.error?.message || responseData.error || `Server error: ${response.status}`);
            }

            // Extract the actual data from the response wrapper
            const data = responseData.data;
            
            // Validate the data structure
            if (!data) {
                console.error('No data object in response');
                throw new Error('Invalid response format from server - no data object');
            }
            
            if (!data.analysis) {
                console.error('No analysis object in data:', data);
                throw new Error('Invalid response format from server - no analysis object');
            }
            
            if (!data.article) {
                console.error('No article object in data:', data);
                throw new Error('Invalid response format from server - no article object');
            }

            // Store the analysis - use the inner data object
            this.currentAnalysis = data;
            currentAnalysis = data;
            window.currentAnalysis = data;
            
            // Also store metadata for later use
            this.currentMetadata = responseData.metadata || {};

            console.log('=== STORED DATA ===');
            console.log('this.currentAnalysis.analysis:', this.currentAnalysis.analysis);
            console.log('Trust score:', this.currentAnalysis.analysis?.trust_score);

            // Complete progress and show results
            this.completeProgress();
            setTimeout(() => {
                this.hideLoading();
                this.displayResults(data);
            }, 1000);

        } catch (error) {
            console.error('Analysis error:', error);
            this.hideLoading();
            
            // Check if it's a site blocking error
            if (error.message && error.message.includes('blocked')) {
                this.showError('It looks like this site is blocking automated analysis. Please use the text option above and copy/paste the entire article to have it analyzed.');
            } else {
                this.showError(`Analysis failed: ${error.message}`);
            }
        } finally {
            isAnalyzing = false;
            this.stopProgressAnimation();
        }
    }

    // Progress Animation Methods
    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('active');
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
    }

    showError(message) {
        const errorEl = document.getElementById('errorMessage');
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.add('active');
            
            setTimeout(() => {
                errorEl.classList.remove('active');
            }, 5000);
        }
    }

    resetProgress() {
        // Reset any progress indicators if needed
    }

    startProgressAnimation() {
        // Start progress animation if implemented
    }

    stopProgressAnimation() {
        // Stop progress animation if implemented
    }

    completeProgress() {
        // Complete progress animation if implemented
    }

    loadSampleData() {
        // Load sample data for development/testing
        console.log('Ready to analyze articles');
    }

    // Helper method to extract scores from nested data
    extractScore(data, fields, defaultValue = 50) {
        if (!data || typeof data !== 'object') return defaultValue;
        
        for (const field of fields) {
            if (data[field] !== undefined && data[field] !== null) {
                const value = parseFloat(data[field]);
                if (!isNaN(value)) return Math.round(value);
            }
        }
        
        return defaultValue;
    }
}

// ============================================================================
// SECTION 3: Initialization
// ============================================================================

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing TruthLens App...');
    
    // Check if dependencies are available
    const missingDeps = [];
    if (typeof AnalysisComponents === 'undefined') {
        missingDeps.push('AnalysisComponents (truthlens-components.js)');
    }
    if (typeof TruthLensDisplay === 'undefined') {
        missingDeps.push('TruthLensDisplay (truthlens-display.js)');
    }
    if (typeof TruthLensServices === 'undefined') {
        missingDeps.push('TruthLensServices (truthlens-services.js)');
    }
    
    if (missingDeps.length > 0) {
        console.warn('Missing dependencies:', missingDeps.join(', '));
        console.warn('Some features may not work properly.');
    }
    
    window.truthLensApp = new TruthLensApp();
});

// Make app available globally
window.TruthLensApp = TruthLensApp;Truthlens-core.js
