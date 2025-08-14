// truthlens-app.js - Main Application File
// This file contains the main app class, initialization, and UI functions

// ============================================================================
// SECTION 1: Configuration and Constants
// ============================================================================

// Global state
let currentAnalysis = null;
let isAnalyzing = false;
let charts = {};
let isPro = true; // For development, keep pro features open

// Service definitions - REMOVED PLAGIARISM DETECTOR
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
// SECTION 2: TruthLensApp Class
// ============================================================================

class TruthLensApp {
    constructor() {
        this.currentAnalysis = null;
        this.isPremium = false;
        this.currentTab = 'url';
        this.API_ENDPOINT = '/api/analyze';
        this.progressInterval = null;
        this.analysisStartTime = null;
        this.analysisComponents = new AnalysisComponents();
        this.timeoutTimer = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('demo')) {
            this.loadDemoArticle();
        }
    }

    setupEventListeners() {
        // Enter key to analyze
        document.getElementById('urlInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.analyzeContent();
        });

        // Text input enter key
        const textInput = document.getElementById('textInput');
        if (textInput) {
            textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    e.preventDefault();
                    this.analyzeContent();
                }
            });
        }

        // Tab switching
        window.switchTab = (tab) => {
            this.currentTab = tab;
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.tab === tab);
            });
            document.querySelectorAll('.tab-content').forEach(content => {
                content.style.display = content.id === `${tab}-tab` ? 'block' : 'none';
            });
            
            if (tab === 'text') {
                document.getElementById('textHelp').style.display = 'block';
            }
        };

        // Global functions
        window.analyzeContent = () => this.analyzeContent();
        window.resetAnalysis = () => this.resetAnalysis();
        window.unlockPremium = () => this.unlockPremium();
        window.downloadPDF = () => this.downloadPDF();
        window.shareAnalysis = () => this.shareAnalysis();
        window.showDemo = () => this.showDemo();
        window.showPricing = () => this.showPricing();
        window.showCapabilities = () => this.showCapabilities();
        window.hideCapabilities = () => this.hideCapabilities();
    }

    resetAnalysis() {
        if (this.timeoutTimer) {
            clearTimeout(this.timeoutTimer);
            this.timeoutTimer = null;
        }
        
        document.getElementById('urlInput').value = '';
        document.getElementById('textInput').value = '';
        
        document.getElementById('resultsSection').style.display = 'none';
        if (document.getElementById('premiumAnalysis')) {
            document.getElementById('premiumAnalysis').style.display = 'none';
        }
        if (document.getElementById('progressSection')) {
            document.getElementById('progressSection').style.display = 'none';
        }
        
        this.hideError();
        
        this.currentTab = 'url';
        if (window.switchTab) {
            window.switchTab('url');
        }
        
        this.currentAnalysis = null;
        
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async analyzeContent() {
        this.analysisStartTime = Date.now();
        
        let input, inputType;
        if (this.currentTab === 'url') {
            input = document.getElementById('urlInput').value.trim();
            inputType = 'url';
            if (!input || !this.isValidUrl(input)) {
                this.showError('Please enter a valid URL');
                return;
            }
        } else {
            input = document.getElementById('textInput').value.trim();
            inputType = 'text';
            if (!input || input.length < 100) {
                this.showError('Please enter at least 100 characters of text');
                return;
            }
        }

        this.hideError();
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
        
        this.showProgress();
        
        const analyzeBtns = document.querySelectorAll('.analyze-btn, .analyze-button');
        analyzeBtns.forEach(btn => {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        });

        this.timeoutTimer = setTimeout(() => {
            console.log('Analysis timeout - site may be blocking access');
            this.handleTimeout(input);
        }, 30000);

        try {
            const response = await fetch(this.API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    [inputType]: input,
                    is_pro: this.isPremium
                })
            });

            if (this.timeoutTimer) {
                clearTimeout(this.timeoutTimer);
                this.timeoutTimer = null;
            }

            if (!response.ok) {
                let errorMessage = 'Analysis failed';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorMessage;
                } catch (e) {
                    console.error('Failed to parse error response:', e);
                }
                throw new Error(errorMessage);
            }

            const responseData = await response.json();
            
            console.log('RAW API RESPONSE:', responseData);
            
            if (responseData.success === false) {
                throw new Error(responseData.error || 'Analysis failed on server');
            }
            
            let analysisData = responseData;
            
            if (responseData.data && typeof responseData.data === 'object') {
                console.log('Data is nested in .data field');
                analysisData = responseData.data;
            }
            
            analysisData = this.normalizeAnalysisData(analysisData);
            
            if (!analysisData.analysis || (!analysisData.analysis.trust_score && analysisData.analysis.trust_score !== 0)) {
                console.error('No trust_score found in analysis');
                throw new Error('Invalid response format: missing trust_score');
            }
            
            this.currentAnalysis = analysisData;
            currentAnalysis = analysisData;
            
            window.debugData = analysisData;
            window.rawResponse = responseData;
            
            this.hideProgress();
            
            this.displayResults(analysisData);
            
            console.log('Analysis complete - Trust Score:', analysisData.analysis.trust_score);
            
        } catch (error) {
            if (this.timeoutTimer) {
                clearTimeout(this.timeoutTimer);
                this.timeoutTimer = null;
            }
            
            console.error('Analysis error:', error);
            this.showError(error.message || 'An error occurred during analysis');
            this.hideProgress();
        } finally {
            analyzeBtns.forEach(btn => {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-search"></i> Analyze';
            });
        }
    }

    handleTimeout(url) {
        this.timeoutTimer = null;
        
        this.hideProgress();
        
        this.showError('This site is blocking our access. Please copy and use the "Text Mode" to enter your article for analysis.');
        
        this.currentTab = 'text';
        if (window.switchTab) {
            window.switchTab('text');
        }
        
        const textInput = document.getElementById('textInput');
        if (textInput) {
            textInput.focus();
        }
        
        const analyzeBtns = document.querySelectorAll('.analyze-btn, .analyze-button');
        analyzeBtns.forEach(btn => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-search"></i> Analyze';
        });
        
        console.log(`Timeout occurred for URL: ${url}`);
    }

    normalizeAnalysisData(data) {
        if (!data.analysis) {
            data.analysis = {
                trust_score: data.trust_score || 50,
                trust_level: data.trust_level || 'Unknown',
                summary: data.summary,
                key_findings: data.key_findings || []
            };
        }

        if (data.detailed_analysis) {
            data.detailed_analysis = DataStructureMapper.mapServiceData(data.detailed_analysis);
        }

        data = this.recalculateTrustScore(data);

        return data;
    }

    recalculateTrustScore(data) {
        const components = [];
        const missingComponents = [];
        
        if (data.detailed_analysis?.source_credibility?.credibility_score !== undefined) {
            components.push({
                name: 'Source Credibility',
                score: data.detailed_analysis.source_credibility.credibility_score,
                weight: 0.25
            });
        } else {
            missingComponents.push('Source Credibility');
        }
        
        if (data.detailed_analysis?.author_analyzer?.credibility_score !== undefined) {
            components.push({
                name: 'Author Credibility',
                score: data.detailed_analysis.author_analyzer.credibility_score,
                weight: 0.20
            });
        } else {
            missingComponents.push('Author Credibility');
        }
        
        if (data.detailed_analysis?.bias_detector?.objectivity_score !== undefined) {
            components.push({
                name: 'Objectivity',
                score: data.detailed_analysis.bias_detector.objectivity_score,
                weight: 0.20
            });
        } else if (data.detailed_analysis?.bias_detector?.overall_bias_score !== undefined) {
            components.push({
                name: 'Objectivity',
                score: 100 - data.detailed_analysis.bias_detector.overall_bias_score,
                weight: 0.20
            });
        } else {
            missingComponents.push('Bias Analysis');
        }
        
        if (data.detailed_analysis?.fact_checker) {
            const normalized = DataStructureMapper.normalizeFactCheckerData(data.detailed_analysis.fact_checker);
            if (normalized.claims_checked > 0) {
                const factScore = (normalized.verified_count / normalized.claims_checked) * 100;
                components.push({
                    name: 'Fact Accuracy',
                    score: factScore,
                    weight: 0.20
                });
            }
        } else {
            missingComponents.push('Fact Checking');
        }
        
        if (components.length >= 2) {
            const totalWeight = components.reduce((sum, c) => sum + c.weight, 0);
            const normalizedScore = components.reduce((sum, c) => 
                sum + (c.score * (c.weight / totalWeight)), 0
            );
            
            if (data.analysis) {
                data.analysis.trust_score = Math.round(normalizedScore);
                data.analysis.recalculated = true;
                data.analysis.missing_components = missingComponents;
                data.analysis.available_components = components.map(c => c.name);
            }
        }
        
        return data;
    }

    showProgress() {
        showLoading();
    }

    hideProgress() {
        hideLoading();
    }

    displayResults(data) {
        console.log('=== DISPLAY RESULTS CALLED ===');
        console.log('Data received:', data);
        
        displayResults(data);
    }

    showError(message) {
        showError(message);
    }

    hideError() {
        hideError();
    }

    isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    async downloadPDF() {
        if (!this.currentAnalysis) {
            this.showError('No analysis available to download');
            return;
        }
        
        downloadPDF();
    }

    shareAnalysis() {
        if (!this.currentAnalysis) return;
        
        shareResults();
    }

    showDemo() {
        this.loadDemoArticle();
    }

    loadDemoArticle() {
        const demoUrls = [
            'https://www.reuters.com/technology/artificial-intelligence/',
            'https://www.bbc.com/news',
            'https://www.npr.org/sections/news/',
            'https://apnews.com/hub/technology'
        ];
        const randomUrl = demoUrls[Math.floor(Math.random() * demoUrls.length)];
        document.getElementById('urlInput').value = randomUrl;
        this.analyzeContent();
    }

    showCapabilities() {
        const capabilitiesSection = document.getElementById('capabilitiesSection');
        if (capabilitiesSection) {
            capabilitiesSection.style.display = 'flex';
        }
    }

    hideCapabilities() {
        const capabilitiesSection = document.getElementById('capabilitiesSection');
        if (capabilitiesSection) {
            capabilitiesSection.style.display = 'none';
        }
    }

    showPricing() {
        this.showError('Premium features coming soon! Get unlimited analysis, PDF reports, and API access.');
        setTimeout(() => this.hideError(), 5000);
    }
}

// ============================================================================
// SECTION 3: Main Functions and Initialization
// ============================================================================

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing TruthLens...');
    
    // Initialize the app
    window.truthLensApp = new TruthLensApp();
    
    // Mode toggle functionality
    const modeBtns = document.querySelectorAll('.mode-btn');
    const urlExplanation = document.getElementById('urlExplanation');
    const textExplanation = document.getElementById('textExplanation');
    const urlInputWrapper = document.getElementById('urlInputWrapper');
    const textInputWrapper = document.getElementById('textInputWrapper');
    
    if (modeBtns.length > 0) {
        modeBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const mode = this.getAttribute('data-mode');
                
                // Update active states
                modeBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                // Toggle explanations
                if (mode === 'url') {
                    if (urlExplanation) urlExplanation.classList.add('active');
                    if (textExplanation) textExplanation.classList.remove('active');
                    if (urlInputWrapper) urlInputWrapper.classList.add('active');
                    if (textInputWrapper) textInputWrapper.classList.remove('active');
                    window.truthLensApp.currentTab = 'url';
                } else {
                    if (urlExplanation) urlExplanation.classList.remove('active');
                    if (textExplanation) textExplanation.classList.add('active');
                    if (urlInputWrapper) urlInputWrapper.classList.remove('active');
                    if (textInputWrapper) textInputWrapper.classList.add('active');
                    window.truthLensApp.currentTab = 'text';
                }
            });
        });
    }
    
    // Reset button functionality
    const resetBtn = document.getElementById('resetBtn');
    const resetTextBtn = document.getElementById('resetTextBtn');
    
    function resetAnalysis() {
        if (window.truthLensApp) {
            window.truthLensApp.resetAnalysis();
        }
    }
    
    if (resetBtn) resetBtn.addEventListener('click', resetAnalysis);
    if (resetTextBtn) resetTextBtn.addEventListener('click', resetAnalysis);
    
    // Add event listener for URL input Enter key
    const urlInput = document.getElementById('urlInput');
    if (urlInput) {
        console.log('URL input found, adding enter key listener');
        urlInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                console.log('Enter key pressed in URL input');
                e.preventDefault();
                analyzeArticle();
            }
        });
    } else {
        console.error('URL input not found!');
    }
    
    // Add click handler for analyze button
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        console.log('Analyze button found, adding click listener');
        analyzeBtn.addEventListener('click', function(e) {
            console.log('Analyze button clicked');
            e.preventDefault();
            analyzeArticle();
        });
    } else {
        console.error('Analyze button not found!');
    }
    
    // Analyze text button
    const analyzeTextBtn = document.getElementById('analyzeTextBtn');
    if (analyzeTextBtn) {
        analyzeTextBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const text = document.getElementById('textInput').value.trim();
            if (!text) {
                showError('Please paste article text to analyze');
                return;
            }
            analyzeArticleText(text);
        });
    }
    
    // Add click handlers for example buttons
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            tryExample(this.getAttribute('data-url'));
        });
    });
    
    // Add click handlers for download and share buttons
    const downloadBtn = document.getElementById('downloadPdfBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            downloadPDF();
        });
    }
    
    const shareBtn = document.getElementById('shareResultsBtn');
    if (shareBtn) {
        shareBtn.addEventListener('click', function(e) {
            e.preventDefault();
            shareResults();
        });
    }
    
    console.log('TruthLens initialization complete');
});

// Main analysis function
async function analyzeArticle() {
    if (window.truthLensApp) {
        window.truthLensApp.currentTab = 'url';
        await window.truthLensApp.analyzeContent();
    }
}

// Analyze article text directly
async function analyzeArticleText(text) {
    if (window.truthLensApp) {
        window.truthLensApp.currentTab = 'text';
        await window.truthLensApp.analyzeContent();
    }
}

// Try example URL
function tryExample(url) {
    document.getElementById('urlInput').value = url;
    document.getElementById('urlInput').focus();
}

// Calculate fact accuracy percentage
function calculateFactAccuracy(factCheckerData) {
    console.log('calculateFactAccuracy called with:', factCheckerData);
    
    if (!factCheckerData || Object.keys(factCheckerData).length === 0) return 0;
    
    const normalized = DataStructureMapper.normalizeFactCheckerData(factCheckerData);
    const { claims_checked: total, verified_count: verified } = normalized;
    
    if (total === 0) return 0;
    return Math.round((verified / total) * 100);
}

// Display article info
function displayArticleInfo(article, analysis) {
    document.getElementById('articleTitle').textContent = article?.title || 'Untitled Article';
    
    const metaHtml = `
        <div class="meta-item">
            <i class="fas fa-user"></i>
            <span>${article?.author || 'Unknown Author'}</span>
        </div>
        <div class="meta-item">
            <i class="fas fa-globe"></i>
            <span>${article?.domain || 'Unknown Source'}</span>
        </div>
        <div class="meta-item">
            <i class="fas fa-calendar"></i>
            <span>${formatDate(article?.publish_date)}</span>
        </div>
        <div class="meta-item">
            <i class="fas fa-clock"></i>
            <span>${Math.ceil((article?.word_count || 0) / 200)} min read</span>
        </div>
    `;
    document.getElementById('articleMeta').innerHTML = metaHtml;
    
    // Display key findings
    const findings = analysis?.key_findings || [];
    
    if (findings.length > 0) {
        let findingsHtml = '<h4 class="key-findings-header">Key Findings</h4>';
        findings.forEach(finding => {
            const type = finding.severity === 'positive' ? 'positive' : 
                       finding.severity === 'high' ? 'negative' : 'warning';
            const icon = type === 'positive' ? 'fa-check-circle' : 
                       type === 'negative' ? 'fa-times-circle' : 'fa-exclamation-circle';
            
            findingsHtml += `
                <div class="finding-item finding-${type}">
                    <i class="fas ${icon}"></i>
                    <span>${escapeHtml(finding.text || finding.finding)}</span>
                </div>
            `;
        });
        document.getElementById('keyFindings').innerHTML = findingsHtml;
    } else {
        document.getElementById('keyFindings').innerHTML = `
            <div class="info-box">
                <div class="info-box-title">
                    <i class="fas fa-info-circle"></i>
                    Analysis Summary
                </div>
                <div class="info-box-content">
                    The detailed analysis of this article is complete. Review the individual service results below for specific insights about credibility, bias, factual accuracy, and more.
                </div>
            </div>
        `;
    }
}

// Display service accordion
function displayServiceAccordion(data) {
    console.log('=== displayServiceAccordion called ===');
    
    const container = document.getElementById('servicesAccordion');
    container.innerHTML = '';
    
    const servicesData = data.detailed_analysis || {};
    
    services.forEach((service, index) => {
        const serviceData = servicesData[service.id] || {};
        
        const accordionItem = createServiceAccordionItem(service, serviceData, index);
        container.appendChild(accordionItem);
    });
}

// Calculate adjusted trust score excluding failed services
function calculateAdjustedTrustScore(servicesData) {
    const scoreComponents = [];
    
    if (servicesData.source_credibility && Object.keys(servicesData.source_credibility).length > 0) {
        const score = extractScore(servicesData.source_credibility, ['credibility_score', 'score']);
        if (score > 0) scoreComponents.push({ name: 'source', score, weight: 0.3 });
    }
    
    if (servicesData.author_analyzer && Object.keys(servicesData.author_analyzer).length > 0) {
        const score = extractScore(servicesData.author_analyzer, ['credibility_score', 'score']);
        if (score > 0) scoreComponents.push({ name: 'author', score, weight: 0.2 });
    }
    
    if (servicesData.bias_detector && Object.keys(servicesData.bias_detector).length > 0) {
        const biasScore = extractScore(servicesData.bias_detector, ['overall_bias_score', 'bias_score'], 0);
        const objectivityScore = 100 - biasScore;
        if (objectivityScore > 0) scoreComponents.push({ name: 'objectivity', score: objectivityScore, weight: 0.25 });
    }
    
    if (servicesData.fact_checker && Object.keys(servicesData.fact_checker).length > 0) {
        const accuracy = calculateFactAccuracy(servicesData.fact_checker);
        if (accuracy > 0) scoreComponents.push({ name: 'facts', score: accuracy, weight: 0.25 });
    }
    
    if (scoreComponents.length === 0) return 0;
    
    const totalWeight = scoreComponents.reduce((sum, comp) => sum + comp.weight, 0);
    
    const adjustedScore = scoreComponents.reduce((sum, comp) => {
        return sum + (comp.score * (comp.weight / totalWeight));
    }, 0);
    
    console.log('Trust score calculation:', {
        components: scoreComponents,
        totalWeight,
        adjustedScore: Math.round(adjustedScore)
    });
    
    return Math.round(adjustedScore);
}

// Display results with enhanced trust score section
function displayResults(data) {
    console.log('displayResults called with:', data);
    
    if (!data) {
        console.error('No data provided to displayResults');
        showError('No analysis data received');
        return;
    }
    
    if (!data.analysis) {
        console.error('Invalid data structure - missing analysis');
        showError('Invalid response format from server');
        return;
    }
    
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.classList.add('active');
    resultsSection.style.display = 'block';
    
    // Display each component with individual error handling
    try {
        displayEnhancedTrustScore(data.analysis, data);
    } catch (e) {
        console.error('Error displaying trust score:', e);
        document.getElementById('trustScoreNumber').textContent = '?';
        document.getElementById('trustSummary').textContent = 'Trust score calculation failed';
    }
    
    try {
        displayArticleInfo(data.article, data.analysis);
    } catch (e) {
        console.error('Error displaying article info:', e);
    }
    
    try {
        displayServiceAccordion(data);
    } catch (e) {
        console.error('Error displaying service accordion:', e);
    }
    
    // Scroll to results smoothly
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// Enhanced trust score display with explanations
function displayEnhancedTrustScore(analysis, fullData) {
    console.log('=== displayEnhancedTrustScore called ===');
    
    if (!analysis) {
        console.error('No analysis data provided to displayEnhancedTrustScore');
        return;
    }
    
    const servicesData = fullData.detailed_analysis || {};
    
    const adjustedScore = calculateAdjustedTrustScore(servicesData);
    const score = adjustedScore || analysis.trust_score || 0;
    const level = getTrustLevel(score);
    
    console.log('Using adjusted trust score:', score);
    
    // Update score number with animation
    animateTrustScore(score);
    
    // Update level indicator
    updateTrustLevelIndicator(score, level);
    
    // Update summary with contextual explanation
    const summaryEl = document.getElementById('trustSummary');
    summaryEl.textContent = getTrustSummaryExplanation(score, level, analysis);
    
    // Count available components
    const availableComponents = [];
    if (servicesData.source_credibility && Object.keys(servicesData.source_credibility).length > 0) {
        availableComponents.push('Source Credibility');
    }
    if (servicesData.author_analyzer && Object.keys(servicesData.author_analyzer).length > 0) {
        availableComponents.push('Author Credibility');
    }
    if (servicesData.bias_detector && Object.keys(servicesData.bias_detector).length > 0) {
        availableComponents.push('Objectivity');
    }
    if (servicesData.fact_checker && Object.keys(servicesData.fact_checker).length > 0) {
        availableComponents.push('Fact Accuracy');
    }
    
    // Update the trust score section heading to reflect actual components
    const trustScoreTitle = document.querySelector('#trustScoreSection h2');
    if (trustScoreTitle) {
        trustScoreTitle.innerHTML = `<i class="fas fa-shield-alt"></i> Trust Score Analysis<br><small style="font-size: 0.6em; font-weight: normal; color: var(--gray-600);">Based on ${availableComponents.length} key components</small>`;
    }
    
    // Create detailed breakdown with explanations
    const breakdownData = [
        {
            id: 'source_credibility',
            icon: 'fa-shield-alt',
            label: 'Source Credibility',
            value: extractScore(servicesData.source_credibility, ['credibility_score', 'score']),
            explanation: getSourceCredibilityExplanation(servicesData.source_credibility),
            hasData: servicesData.source_credibility && Object.keys(servicesData.source_credibility).length > 0
        },
        {
            id: 'author_credibility',
            icon: 'fa-user-check',
            label: 'Author Credibility',
            value: extractScore(servicesData.author_analyzer, ['credibility_score', 'score']),
            explanation: getAuthorCredibilityExplanation(servicesData.author_analyzer),
            hasData: servicesData.author_analyzer && Object.keys(servicesData.author_analyzer).length > 0
        },
        {
            id: 'objectivity',
            icon: 'fa-balance-scale',
            label: 'Objectivity Score',
            value: 100 - extractScore(servicesData.bias_detector, ['overall_bias_score', 'bias_score'], 0),
            explanation: getObjectivityExplanation(servicesData.bias_detector),
            hasData: servicesData.bias_detector && Object.keys(servicesData.bias_detector).length > 0
        },
        {
            id: 'fact_accuracy',
            icon: 'fa-check-double',
            label: 'Fact Accuracy',
            value: calculateFactAccuracy(servicesData.fact_checker),
            explanation: getFactAccuracyExplanation(servicesData.fact_checker),
            hasData: servicesData.fact_checker && Object.keys(servicesData.fact_checker).length > 0
        }
    ];
    
    let breakdownHtml = '';
    breakdownData.forEach(item => {
        if (!item.hasData) {
            breakdownHtml += `
                <div class="breakdown-item breakdown-unavailable" style="opacity: 0.6;">
                    <div class="breakdown-header">
                        <div class="breakdown-label">
                            <div class="breakdown-icon">
                                <i class="fas ${item.icon}"></i>
                            </div>
                            <span>${item.label}</span>
                        </div>
                        <div class="breakdown-value">N/A</div>
                    </div>
                    <div class="breakdown-explanation">Unable to analyze - service unavailable</div>
                    <div class="breakdown-bar">
                        <div class="breakdown-fill" style="width: 0%; background: #ccc;"></div>
                    </div>
                </div>
            `;
        } else {
            const type = getBreakdownType(item.value);
            breakdownHtml += `
                <div class="breakdown-item breakdown-${type}">
                    <div class="breakdown-header">
                        <div class="breakdown-label">
                            <div class="breakdown-icon">
                                <i class="fas ${item.icon}"></i>
                            </div>
                            <span>${item.label}</span>
                        </div>
                        <div class="breakdown-value">${item.value}%</div>
                    </div>
                    <div class="breakdown-explanation">${item.explanation}</div>
                    <div class="breakdown-bar">
                        <div class="breakdown-fill" style="width: 0%;" data-target="${item.value}"></div>
                    </div>
                </div>
            `;
        }
    });
    
    document.getElementById('trustBreakdown').innerHTML = breakdownHtml;
    
    // Animate breakdown bars after DOM update
    setTimeout(() => {
        document.querySelectorAll('.breakdown-fill').forEach(bar => {
            const target = bar.getAttribute('data-target');
            bar.style.width = target + '%';
        });
    }, 100);
    
    // Create enhanced gauge chart
    createEnhancedTrustGauge(score);
}

// ============================================================================
// SECTION 4: UI Functions
// ============================================================================

// Animate trust score number
function animateTrustScore(targetScore) {
    const scoreEl = document.getElementById('trustScoreNumber');
    if (!scoreEl) {
        console.error('trustScoreNumber element not found');
        return;
    }
    
    let currentScore = 0;
    const increment = targetScore / 50;
    const interval = setInterval(() => {
        currentScore += increment;
        if (currentScore >= targetScore) {
            currentScore = targetScore;
            clearInterval(interval);
        }
        scoreEl.textContent = Math.round(currentScore);
        scoreEl.style.color = getScoreColor(currentScore);
    }, 20);
}

// Update trust level indicator
function updateTrustLevelIndicator(score, level) {
    const iconEl = document.getElementById('trustLevelIcon');
    const textEl = document.getElementById('trustLevelText');
    const indicatorEl = document.getElementById('trustLevelIndicator');
    
    if (!iconEl || !textEl || !indicatorEl) {
        console.error('Trust level indicator elements not found');
        return;
    }
    
    // Set text
    textEl.textContent = level;
    
    // Set color and icon based on score
    if (score >= 80) {
        iconEl.className = 'fas fa-check-circle trust-level-icon';
        iconEl.style.color = 'var(--accent)';
        indicatorEl.style.background = 'rgba(16, 185, 129, 0.1)';
        indicatorEl.style.border = '2px solid var(--accent)';
    } else if (score >= 60) {
        iconEl.className = 'fas fa-exclamation-circle trust-level-icon';
        iconEl.style.color = 'var(--info)';
        indicatorEl.style.background = 'rgba(59, 130, 246, 0.1)';
        indicatorEl.style.border = '2px solid var(--info)';
    } else if (score >= 40) {
        iconEl.className = 'fas fa-exclamation-triangle trust-level-icon';
        iconEl.style.color = 'var(--warning)';
        indicatorEl.style.background = 'rgba(245, 158, 11, 0.1)';
        indicatorEl.style.border = '2px solid var(--warning)';
    } else {
        iconEl.className = 'fas fa-times-circle trust-level-icon';
        iconEl.style.color = 'var(--danger)';
        indicatorEl.style.background = 'rgba(239, 68, 68, 0.1)';
        indicatorEl.style.border = '2px solid var(--danger)';
    }
}

// FIXED: Create enhanced trust gauge without overlapping text
function createEnhancedTrustGauge(score) {
    const canvas = document.getElementById('trustGauge');
    if (!canvas) {
        console.error('trustGauge canvas element not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Ensure charts object exists
    if (typeof charts === 'undefined') {
        window.charts = {};
    }
    
    if (charts.trustGauge) {
        charts.trustGauge.destroy();
    }
    
    // Create gradient based on score
    const gradient = ctx.createLinearGradient(0, 0, 300, 0);
    if (score >= 80) {
        gradient.addColorStop(0, '#10b981');
        gradient.addColorStop(1, '#059669');
    } else if (score >= 60) {
        gradient.addColorStop(0, '#3b82f6');
        gradient.addColorStop(1, '#2563eb');
    } else if (score >= 40) {
        gradient.addColorStop(0, '#f59e0b');
        gradient.addColorStop(1, '#d97706');
    } else {
        gradient.addColorStop(0, '#ef4444');
        gradient.addColorStop(1, '#dc2626');
    }
    
    // Create chart WITHOUT the afterDraw plugin that draws the score
    charts.trustGauge = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [gradient, '#E5E7EB'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            circumference: 180,
            rotation: -90,
            cutout: '80%',
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        }
        // REMOVED the plugins array that was drawing text
    });
}

// Create service accordion item - FIXED with proper chevron icon
function createServiceAccordionItem(service, serviceData, index) {
    const item = document.createElement('div');
    item.className = 'service-accordion-item';
    item.id = `service-${service.id}`;
    
    // Add data state indicator
    const hasData = serviceData && Object.keys(serviceData).length > 0;
    const dataStateClass = hasData ? '' : 'no-data';
    
    // Extract preview data
    const previewData = getServicePreviewData(service.id, serviceData);
    
    item.innerHTML = `
        <div class="service-accordion-header" onclick="toggleAccordion('${service.id}', event)">
            <div class="data-state-indicator ${dataStateClass}"></div>
            <div class="service-header-content">
                <div class="service-icon-wrapper">
                    <i class="fas ${service.icon}"></i>
                </div>
                <div class="service-info">
                    <h3 class="service-name">${service.name}</h3>
                    <p class="service-description">${service.description}</p>
                    <div class="service-preview">
                        ${previewData.map(preview => `
                            <div class="preview-item">
                                <span class="preview-label">${preview.label}:</span>
                                <span class="preview-value" style="color: ${preview.color || 'inherit'}">
                                    ${preview.value}
                                </span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
            ${service.isPro && !isPro ? 
                '<div class="pro-badge"><i class="fas fa-crown"></i> Pro</div>' : 
                '<i class="fas fa-chevron-down service-expand-icon"></i>'
            }
        </div>
        <div class="service-accordion-content">
            <div class="service-content-inner">
                ${hasData ? 
                    renderDetailedServiceContent(service.id, serviceData) : 
                    '<div class="no-data-message">Service analysis unavailable for this article.</div>'
                }
            </div>
        </div>
    `;
    
    return item;
}

// Get service preview data
function getServicePreviewData(serviceId, data) {
    if (!data || Object.keys(data).length === 0) {
        return [{ label: 'Status', value: 'Not Available', color: '#6b7280' }];
    }
    
    switch (serviceId) {
        case 'source_credibility':
            const sourceScore = extractScore(data, ['credibility_score', 'score']);
            const sourceName = data.source_name || data.name || 'Unknown';
            return [
                { label: 'Source', value: sourceName },
                { label: 'Score', value: `${sourceScore}%`, color: getScoreColor(sourceScore) }
            ];
            
        case 'author_analyzer':
            const authorScore = extractScore(data, ['credibility_score', 'score']);
            const authorName = data.author_name || data.name || 'Unknown';
            const verified = data.verification_status?.verified ? '✓' : '✗';
            return [
                { label: 'Author', value: authorName },
                { label: 'Verified', value: verified, color: verified === '✓' ? '#10b981' : '#ef4444' },
                { label: 'Score', value: `${authorScore}%`, color: getScoreColor(authorScore) }
            ];
            
        case 'bias_detector':
            const biasScore = extractScore(data, ['overall_bias_score', 'bias_score'], 0);
            const objectivity = 100 - biasScore;
            const biasLevel = data.bias_level || getBiasLevel(biasScore);
            return [
                { label: 'Bias Level', value: biasLevel, color: getBiasColor(biasScore) },
                { label: 'Objectivity', value: `${objectivity}%`, color: getScoreColor(objectivity) }
            ];
            
        case 'fact_checker':
            const normalized = DataStructureMapper.normalizeFactCheckerData(data);
            const accuracy = normalized.claims_checked > 0 ? 
                Math.round((normalized.verified_count / normalized.claims_checked) * 100) : 0;
            return [
                { label: 'Claims Checked', value: normalized.claims_checked },
                { label: 'Accuracy', value: `${accuracy}%`, color: getScoreColor(accuracy) }
            ];
            
        case 'transparency_analyzer':
            const transparencyScore = extractScore(data, ['transparency_score', 'score']);
            const indicators = [
                data.has_author !== false,
                data.has_date !== false,
                data.has_sources !== false
            ].filter(Boolean).length;
            return [
                { label: 'Transparency', value: `${transparencyScore}%`, color: getScoreColor(transparencyScore) },
                { label: 'Indicators', value: `${indicators}/3` }
            ];
            
        case 'manipulation_detector':
            const manipulationLevel = data.manipulation_level || data.level || 'Unknown';
            const techniquesCount = data.techniques_count || 
                (data.techniques && data.techniques.length) || 0;
            return [
                { label: 'Level', value: manipulationLevel, 
                  color: manipulationLevel.toLowerCase() === 'low' || manipulationLevel.toLowerCase() === 'minimal' ? '#10b981' : 
                         manipulationLevel.toLowerCase() === 'moderate' ? '#f59e0b' : '#ef4444' },
                { label: 'Techniques', value: techniquesCount }
            ];
            
        case 'content_analyzer':
            const qualityScore = extractScore(data, ['quality_score', 'score']);
            const readabilityScore = extractScore(data.readability || {}, ['score']);
            return [
                { label: 'Quality', value: `${qualityScore}%`, color: getScoreColor(qualityScore) },
                { label: 'Readability', value: `${readabilityScore}%`, color: getScoreColor(readabilityScore) }
            ];
            
        default:
            return [{ label: 'Status', value: 'Analysis Complete' }];
    }
}

// Update service visualizations
function updateServiceVisualizations(serviceId) {
    const serviceData = currentAnalysis?.detailed_analysis?.[serviceId] || {};
    if (!serviceData || Object.keys(serviceData).length === 0) return;
    
    // Find all canvases in this service section
    const canvases = document.querySelectorAll(`#service-${serviceId} canvas`);
    canvases.forEach(canvas => {
        const chartType = canvas.getAttribute('data-chart-type');
        const chartData = canvas.getAttribute('data-chart-data');
        if (chartType && chartData) {
            try {
                createServiceChart(canvas, chartType, JSON.parse(chartData));
            } catch (e) {
                console.error(`Failed to create chart for ${serviceId}:`, e);
            }
        }
    });
}

// Create service chart
function createServiceChart(canvas, type, data) {
    const ctx = canvas.getContext('2d');
    const chartId = canvas.id;
    
    // Ensure charts object exists
    if (typeof charts === 'undefined') {
        window.charts = {};
    }
    
    // Destroy existing chart
    if (charts[chartId]) {
        charts[chartId].destroy();
    }
    
    // Create new chart based on type
    let config;
    switch (type) {
        case 'radar':
            config = createRadarChartConfig(data);
            break;
        case 'polarArea':
            config = createPolarAreaChartConfig(data);
            break;
        case 'bar':
            config = createBarChartConfig(data);
            break;
        default:
            console.error('Unknown chart type:', type);
            return;
    }
    
    charts[chartId] = new Chart(ctx, config);
}

// Toggle accordion function - MUST BE DEFINED BEFORE createServiceAccordionItem
function toggleAccordion(serviceId, event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    // Save current scroll position
    const currentScrollY = window.scrollY;
    
    const item = document.getElementById(`service-${serviceId}`);
    const isActive = item.classList.contains('active');
    
    // Close all other items
    document.querySelectorAll('.service-accordion-item').forEach(el => {
        if (el.id !== `service-${serviceId}`) {
            el.classList.remove('active');
        }
    });
    
    // Toggle current item
    item.classList.toggle('active');
    
    // Restore scroll position
    window.scrollTo(0, currentScrollY);
    
    // If opening, create/update visualizations after animation
    if (!isActive) {
        setTimeout(() => {
            updateServiceVisualizations(serviceId);
        }, 300);
    }
}

// Make toggleAccordion function global so onclick can access it
window.toggleAccordion = toggleAccordion;

// Enhanced PDF download
async function downloadPDF() {
    if (!currentAnalysis || !currentAnalysis.analysis || !currentAnalysis.article) {
        showError('No analysis available to download');
        return;
    }
    
    showLoading();
    
    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        let yPosition = 20;
        const lineHeight = 7;
        const pageHeight = doc.internal.pageSize.height;
        const pageWidth = doc.internal.pageSize.width;
        const margin = 20;
        const contentWidth = pageWidth - (2 * margin);
        
        // Helper function to add text with page break check
        function addText(text, fontSize = 12, fontStyle = 'normal', indent = 0) {
            doc.setFontSize(fontSize);
            doc.setFont(undefined, fontStyle);
            
            const lines = doc.splitTextToSize(text, contentWidth - indent);
            
            lines.forEach(line => {
                if (yPosition > pageHeight - 30) {
                    doc.addPage();
                    yPosition = 20;
                }
                doc.text(line, margin + indent, yPosition);
                yPosition += fontSize === 12 ? lineHeight : lineHeight + 2;
            });
        }
        
        // Title Page
        doc.setFillColor(99, 102, 241);
        doc.rect(0, 0, pageWidth, 60, 'F');
        
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(24);
        doc.setFont(undefined, 'bold');
        doc.text('TruthLens AI Analysis Report', pageWidth / 2, 30, { align: 'center' });
        
        doc.setFontSize(14);
        doc.setFont(undefined, 'normal');
        doc.text('Professional News Verification', pageWidth / 2, 45, { align: 'center' });
        
        doc.setTextColor(0, 0, 0);
        yPosition = 80;
        
        // Executive Summary
        addText('EXECUTIVE SUMMARY', 18, 'bold');
        yPosition += 5;
        
        addText(`URL: ${document.getElementById('urlInput').value}`, 12);
        addText(`Analysis Date: ${new Date().toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })}`, 12);
        
        yPosition += 10;
        
        // Trust Score Box
        doc.setFillColor(240, 240, 240);
        doc.rect(margin, yPosition, contentWidth, 40, 'F');
        
        // Calculate adjusted trust score
        const adjustedScore = calculateAdjustedTrustScore(currentAnalysis.detailed_analysis || {});
        const displayScore = adjustedScore || currentAnalysis.analysis.trust_score || 0;
        
        doc.setFontSize(16);
        doc.setFont(undefined, 'bold');
        doc.text(`Overall Trust Score: ${displayScore}/100`, margin + 10, yPosition + 15);
        
        doc.setFontSize(14);
        doc.text(`Trust Level: ${getTrustLevel(displayScore)}`, margin + 10, yPosition + 30);
        
        yPosition += 50;
        
        // Article Information
        addText('ARTICLE INFORMATION', 16, 'bold');
        yPosition += 5;
        
        addText(`Title: ${currentAnalysis.article.title || 'Unknown'}`, 12);
        addText(`Author: ${currentAnalysis.article.author || 'Unknown'}`, 12);
        addText(`Source: ${currentAnalysis.article.domain || 'Unknown'}`, 12);
        addText(`Publication Date: ${formatDate(currentAnalysis.article.publish_date)}`, 12);
        addText(`Word Count: ${currentAnalysis.article.word_count || 'Unknown'}`, 12);
        
        yPosition += 10;
        
        // Trust Score Analysis
        addText('TRUST SCORE ANALYSIS', 16, 'bold');
        yPosition += 5;
        addText(getTrustSummaryExplanation(displayScore, getTrustLevel(displayScore), currentAnalysis.analysis), 12);
        
        yPosition += 10;
        
        // Component Scores
        addText('TRUST COMPONENTS', 16, 'bold');
        yPosition += 5;
        
        const detailedAnalysis = currentAnalysis.detailed_analysis || {};
        const components = [
            {
                name: 'Source Credibility',
                score: extractScore(detailedAnalysis.source_credibility, ['credibility_score', 'score']),
                explanation: getSourceCredibilityExplanation(detailedAnalysis.source_credibility)
            },
            {
                name: 'Author Credibility',
                score: extractScore(detailedAnalysis.author_analyzer, ['credibility_score', 'score']),
                explanation: getAuthorCredibilityExplanation(detailedAnalysis.author_analyzer)
            },
            {
                name: 'Objectivity Score',
                score: 100 - extractScore(detailedAnalysis.bias_detector, ['overall_bias_score', 'bias_score'], 0),
                explanation: getObjectivityExplanation(detailedAnalysis.bias_detector)
            },
            {
                name: 'Fact Accuracy',
                score: calculateFactAccuracy(detailedAnalysis.fact_checker),
                explanation: getFactAccuracyExplanation(detailedAnalysis.fact_checker)
            }
        ];
        
        components.forEach(comp => {
            addText(`${comp.name}: ${comp.score}%`, 12, 'bold');
            addText(comp.explanation, 11, 'normal', 5);
            yPosition += 3;
        });
        
        // Key Findings
        if (currentAnalysis.analysis.key_findings && currentAnalysis.analysis.key_findings.length > 0) {
            yPosition += 10;
            addText('KEY FINDINGS', 16, 'bold');
            yPosition += 5;
            
            currentAnalysis.analysis.key_findings.forEach((finding, index) => {
                const findingText = `${index + 1}. ${finding.text || finding.finding}`;
                const severity = finding.severity === 'positive' ? '✓' : 
                               finding.severity === 'high' ? '⚠' : '•';
                addText(`${severity} ${findingText}`, 12, 'normal', 5);
            });
        }
        
        // New page for detailed analysis
        doc.addPage();
        yPosition = 20;
        
        addText('DETAILED ANALYSIS', 18, 'bold');
        yPosition += 10;
        
        // Process each service
        services.forEach(service => {
            const serviceData = detailedAnalysis[service.id];
            if (!serviceData || Object.keys(serviceData).length === 0) return;
            
            // Add page break if needed
            if (yPosition > pageHeight - 80) {
                doc.addPage();
                yPosition = 20;
            }
            
            // Service header
            doc.setFillColor(245, 245, 245);
            doc.rect(margin, yPosition, contentWidth, 10, 'F');
            addText(service.name.toUpperCase(), 14, 'bold');
            yPosition += 5;
            
            // Service-specific content
            const previewData = getServicePreviewData(service.id, serviceData);
            previewData.forEach(item => {
                addText(`${item.label}: ${item.value}`, 12);
            });
            
            yPosition += 10;
        });
        
        // Footer
        doc.setFontSize(10);
        doc.setTextColor(128, 128, 128);
        const totalPages = doc.internal.getNumberOfPages();
        
        for (let i = 1; i <= totalPages; i++) {
            doc.setPage(i);
            doc.text(
                `Page ${i} of ${totalPages} | Generated by TruthLens AI | ${new Date().toLocaleDateString()}`,
                pageWidth / 2,
                pageHeight - 10,
                { align: 'center' }
            );
        }
        
        // Save the PDF
        const fileName = `truthlens-analysis-${Date.now()}.pdf`;
        doc.save(fileName);
        
    } catch (error) {
        console.error('PDF generation error:', error);
        showError('Failed to generate PDF report. Please try again.');
    } finally {
        hideLoading();
    }
}

// Share results
function shareResults() {
    if (!currentAnalysis || !currentAnalysis.analysis) {
        showError('No analysis available to share');
        return;
    }
    
    const adjustedScore = calculateAdjustedTrustScore(currentAnalysis.detailed_analysis || {});
    const trustScore = adjustedScore || currentAnalysis.analysis.trust_score || 0;
    const articleTitle = currentAnalysis.article.title || 'Article';
    
    const shareText = `TruthLens AI Analysis: "${articleTitle}" scored ${trustScore}/100 for trustworthiness. Check out the detailed analysis:`;
    
    if (navigator.share) {
        navigator.share({
            title: 'TruthLens AI Analysis',
            text: shareText,
            url: window.location.href
        }).catch(err => {
            console.log('Share cancelled:', err);
        });
    } else {
        // Fallback: Copy link to clipboard
        const url = window.location.href;
        navigator.clipboard.writeText(`${shareText} ${url}`).then(() => {
            showError('Analysis link copied to clipboard!');
            setTimeout(hideError, 3000);
        }).catch(() => {
            showError('Sharing is not supported on this device');
        });
    }
}

// Add shake animation and additional styles
const shakeStyle = document.createElement('style');
shakeStyle.innerHTML = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    
    /* Trust factor styles for enhanced display */
    .trust-factor-detailed {
        background: white;
        border-radius: var(--radius);
        padding: var(--space-md);
        margin-bottom: var(--space-md);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
        opacity: 0;
        animation: fadeInUp 0.6s forwards;
    }
    
    .trust-factor-detailed:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    
    .factor-main {
        margin-bottom: var(--space-md);
    }
    
    .factor-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--space-sm);
    }
    
    .factor-info {
        display: flex;
        align-items: center;
        gap: var(--space-sm);
    }
    
    .factor-info i {
        font-size: 1.25rem;
    }
    
    .factor-name {
        font-weight: 600;
        font-size: 1rem;
        color: var(--gray-900);
    }
    
    .factor-score-display {
        text-align: right;
    }
    
    .factor-score-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--gray-900);
    }
    
    .factor-score-label {
        font-size: 0.75rem;
        color: var(--gray-600);
    }
    
    .factor-bar {
        height: 8px;
        background: var(--gray-200);
        border-radius: 4px;
        overflow: hidden;
    }
    
    .factor-fill {
        height: 100%;
        transition: all 1s ease-out;
        border-radius: 4px;
    }
    
    .factor-analysis-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: var(--space-sm);
    }
    
    .analysis-box-header h5 {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--gray-900);
        margin: 0;
    }
    
    .analysis-box p {
        font-size: 0.813rem;
        color: var(--gray-700);
        line-height: 1.5;
        margin: 0;
    }
    
    .score-high { color: var(--accent); }
    .score-medium { color: var(--info); }
    .score-low { color: var(--warning); }
    .score-very-low { color: var(--danger); }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Additional CSS for proper rendering */
    .recent-articles-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .recent-article-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem;
        background: var(--gray-50);
        border-radius: var(--radius-sm);
        font-size: 0.813rem;
    }
    
    .article-title {
        flex: 1;
        font-weight: 500;
        color: var(--gray-900);
    }
    
    .article-date {
        color: var(--gray-600);
        font-size: 0.75rem;
    }
    
    .loaded-phrases-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .loaded-phrase-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem;
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: var(--radius-sm);
    }
    
    .phrase-text {
        font-style: italic;
        color: var(--gray-700);
        font-size: 0.813rem;
    }
    
    .phrase-severity {
        padding: 0.125rem 0.5rem;
        border-radius: 999px;
        font-size: 0.625rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .severity-high { 
        background: rgba(239, 68, 68, 0.1); 
        color: var(--danger); 
    }
    
    .severity-medium { 
        background: rgba(245, 158, 11, 0.1); 
        color: var(--warning); 
    }
    
    .severity-low { 
        background: rgba(59, 130, 246, 0.1); 
        color: var(--info); 
    }
    
    .transparency-checklist {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .checklist-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
        border-radius: var(--radius-sm);
        font-size: 0.813rem;
    }
    
    .checklist-pass {
        background: rgba(16, 185, 129, 0.1);
        color: var(--accent);
    }
    
    .checklist-fail {
        background: rgba(239, 68, 68, 0.1);
        color: var(--danger);
    }
    
    .checklist-item i {
        font-size: 0.875rem;
    }
    
    .empty-state {
        text-align: center;
        padding: 2rem;
        background: var(--gray-50);
        border-radius: var(--radius);
    }
    
    .empty-state i {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    .success-state {
        background: rgba(16, 185, 129, 0.1);
    }
    
    .success-state i {
        color: var(--accent);
    }
    
    .empty-state-text {
        font-weight: 600;
        color: var(--gray-900);
        margin-bottom: 0.5rem;
    }
    
    .empty-state-subtext {
        color: var(--gray-600);
        font-size: 0.875rem;
    }
`;
document.head.appendChild(shakeStyle);

// Console branding - UPDATED FOR 7 SERVICES
console.log('%cTruthLens AI', 'font-size: 24px; font-weight: bold; color: #6366f1;');
console.log('%cProfessional News Analysis', 'font-size: 14px; color: #6b7280;');
console.log('%cPowered by 7 Specialized AI Services', 'font-size: 12px; color: #10b981;');
console.log('%cType window.debugData in console after analysis to explore the data', 'font-size: 12px; color: #f59e0b');
console.log('%cType window.rawResponse to see the raw API response', 'font-size: 12px; color: #f59e0b');box {
        background: var(--gray-50);
        border-radius: var(--radius-sm);
        padding: var(--space-sm);
        border-left: 3px solid var(--primary);
    }
    
    .analysis-box-header {
        display: flex;
        align-items: center;
        gap: var(--space-xs);
        margin-bottom: var(--space-xs);
    }
    
    .analysis-box-header i {
        color: var(--primary);
        font-size: 0.875rem;
    }
    
    .analysis-
