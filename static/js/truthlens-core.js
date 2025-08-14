// truthlens-core.js - Core Application Logic and API Communication
// FIXED VERSION: Addresses all trust score calculation and service handling issues

// ============================================================================
// SECTION 1: Configuration and Constants
// ============================================================================

// Global state
let currentAnalysis = null;
let isAnalyzing = false;
let charts = {};
let isPro = true; // For development, keep pro features open

// Service definitions with proper weighting
const services = [
    {
        id: 'source_credibility',
        name: 'Source Credibility',
        icon: 'fa-shield-alt',
        description: 'Evaluates the reliability and trustworthiness of the news source',
        isPro: false,
        weight: 0.25  // 25% of total score
    },
    {
        id: 'author_analyzer',
        name: 'Author Analysis',
        icon: 'fa-user-check',
        description: 'Analyzes author credentials and publishing history',
        isPro: false,
        weight: 0.20  // 20% of total score
    },
    {
        id: 'bias_detector',
        name: 'Bias Detection',
        icon: 'fa-balance-scale',
        description: 'Identifies political, ideological, and narrative biases',
        isPro: true,
        weight: 0.15  // 15% of total score
    },
    {
        id: 'fact_checker',
        name: 'Fact Verification',
        icon: 'fa-check-double',
        description: 'Verifies claims against trusted fact-checking databases',
        isPro: true,
        weight: 0.20  // 20% of total score
    },
    {
        id: 'transparency_analyzer',
        name: 'Transparency Analysis',
        icon: 'fa-eye',
        description: 'Evaluates source disclosure and funding transparency',
        isPro: true,
        weight: 0.10  // 10% of total score
    },
    {
        id: 'manipulation_detector',
        name: 'Manipulation Detection',
        icon: 'fa-mask',
        description: 'Detects emotional manipulation and propaganda techniques',
        isPro: true,
        weight: 0.10  // 10% of total score
    },
    {
        id: 'content_analyzer',
        name: 'Content Analysis',
        icon: 'fa-file-alt',
        description: 'Analyzes writing quality, structure, and coherence',
        isPro: true,
        weight: 0.05  // 5% of total score (not included in trust score but analyzed)
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
        console.log('TruthLens initialized with enhanced trust score calculation');
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

        // Analyze buttons - with null check
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

        // Example buttons - removed site blocking message handlers
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
            
            // Debug logging
            console.log('API Response:', responseData);
            
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

            // FIXED: Recalculate trust score based on available services
            const recalculatedScore = this.calculateTrustScore(data.detailed_analysis);
            if (recalculatedScore !== null) {
                data.analysis.trust_score = recalculatedScore;
                data.analysis.trust_level = this.getTrustLevel(recalculatedScore);
                console.log('Recalculated trust score:', recalculatedScore);
            }

            // Store the analysis
            this.currentAnalysis = data;
            currentAnalysis = data;
            window.currentAnalysis = data;
            
            // Store metadata for later use
            this.currentMetadata = responseData.metadata || {};

            // Complete progress and show results
            this.completeProgress();
            setTimeout(() => {
                this.hideLoading();
                this.displayResults(data);
            }, 1000);

        } catch (error) {
            console.error('Analysis error:', error);
            this.hideLoading();
            this.showError(`Analysis failed: ${error.message}`);
        } finally {
            isAnalyzing = false;
            this.stopProgressAnimation();
        }
    }

    // FIXED: New method to calculate trust score based on available services
    calculateTrustScore(detailedAnalysis) {
        if (!detailedAnalysis || typeof detailedAnalysis !== 'object') {
            return null;
        }

        let totalWeight = 0;
        let weightedScore = 0;
        const serviceScores = {};

        // Define score extraction for each service
        const scoreExtractors = {
            source_credibility: (data) => {
                const score = this.extractScore(data, ['credibility_score', 'score'], null);
                return score !== null ? score : null;
            },
            author_analyzer: (data) => {
                const score = this.extractScore(data, ['author_score', 'score', 'credibility_score'], null);
                // If we have minimal data (just author name), don't penalize
                if (score === null && data.author_name) {
                    return 50; // Neutral score for unknown authors
                }
                return score;
            },
            bias_detector: (data) => {
                const biasScore = this.extractScore(data, ['bias_score', 'score', 'overall_bias_score'], null);
                // Convert bias to objectivity (lower bias = higher objectivity)
                return biasScore !== null ? (100 - biasScore) : null;
            },
            fact_checker: (data) => {
                if (data.fact_checks && Array.isArray(data.fact_checks)) {
                    const total = data.fact_checks.length;
                    if (total === 0) return 100; // No claims to check = no false claims
                    const verified = data.fact_checks.filter(c => 
                        c.verdict === 'True' || c.verdict === 'Verified' || c.verdict === 'true'
                    ).length;
                    return Math.round((verified / total) * 100);
                }
                return this.extractScore(data, ['accuracy_score', 'score'], null);
            },
            transparency_analyzer: (data) => {
                return this.extractScore(data, ['transparency_score', 'score'], null);
            },
            manipulation_detector: (data) => {
                const manipScore = this.extractScore(data, ['manipulation_score', 'score'], null);
                if (manipScore !== null) {
                    // Convert manipulation to integrity (lower manipulation = higher integrity)
                    return 100 - manipScore;
                }
                // Check for manipulation level
                if (data.manipulation_level) {
                    const levels = { 'Low': 90, 'Minimal': 95, 'Moderate': 50, 'High': 20, 'Extreme': 10 };
                    return levels[data.manipulation_level] || 50;
                }
                return null;
            }
        };

        // Calculate scores for each service
        services.forEach(service => {
            // Skip content analyzer for trust score (it's informational only)
            if (service.id === 'content_analyzer') {
                return;
            }

            const serviceData = detailedAnalysis[service.id];
            if (!serviceData || Object.keys(serviceData).length === 0) {
                console.log(`Service ${service.id} has no data, skipping`);
                return;
            }

            const extractor = scoreExtractors[service.id];
            if (extractor) {
                const score = extractor(serviceData);
                if (score !== null && !isNaN(score)) {
                    serviceScores[service.id] = score;
                    weightedScore += score * service.weight;
                    totalWeight += service.weight;
                    console.log(`${service.id}: score=${score}, weight=${service.weight}`);
                }
            }
        });

        // If we have at least 2 services with scores, calculate weighted average
        if (Object.keys(serviceScores).length >= 2 && totalWeight > 0) {
            const finalScore = Math.round(weightedScore / totalWeight);
            console.log('Service scores:', serviceScores);
            console.log('Total weight:', totalWeight);
            console.log('Final trust score:', finalScore);
            return finalScore;
        }

        // If we only have source credibility, use it but cap at 75
        if (serviceScores.source_credibility && Object.keys(serviceScores).length === 1) {
            return Math.min(75, serviceScores.source_credibility);
        }

        return null;
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

    // Get trust level based on score
    getTrustLevel(score) {
        if (score >= 80) return 'Very High';
        if (score >= 60) return 'High';
        if (score >= 40) return 'Moderate';
        if (score >= 20) return 'Low';
        return 'Very Low';
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
        // Reset progress indicators
        const progressSteps = document.querySelectorAll('.progress-step');
        progressSteps.forEach(step => {
            step.classList.remove('active', 'complete');
        });
    }

    startProgressAnimation() {
        let currentStep = 0;
        const steps = document.querySelectorAll('.progress-step');
        const totalSteps = steps.length;
        
        this.progressInterval = setInterval(() => {
            if (currentStep < totalSteps) {
                steps[currentStep].classList.add('active');
                currentStep++;
            } else {
                // Keep cycling through steps
                steps.forEach(step => step.classList.remove('active'));
                currentStep = 0;
            }
        }, 500);
    }

    stopProgressAnimation() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }

    completeProgress() {
        this.stopProgressAnimation();
        const steps = document.querySelectorAll('.progress-step');
        steps.forEach(step => {
            step.classList.remove('active');
            step.classList.add('complete');
        });
    }

    loadSampleData() {
        // Ready to analyze articles
        console.log('Ready to analyze articles with enhanced trust scoring');
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
window.TruthLensApp = TruthLensApp;
