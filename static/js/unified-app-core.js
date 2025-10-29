/**
 * TruthLens Unified App Core
 * Version: 6.11.0 - POSITIVE PROGRESS MESSAGES FIX
 * Date: October 28, 2025
 * 
 * CHANGES FROM 6.10.0:
 * ✅ FIXED: Changed scary/negative progress messages to positive, exciting ones
 * ✅ REMOVED: "Detecting potential bias..." and similar negative phrases
 * ✅ ADDED: Exciting, upbeat messages that make users feel good
 * ✅ PRESERVED: All v6.10.0 functionality (DO NO HARM ✓)
 * 
 * WHAT'S NEW IN v6.11.0:
 * - Progress messages are now positive and engaging
 * - Messages highlight what we're discovering, not what we're "detecting"
 * - Makes the loading experience feel exciting instead of scary
 * 
 * Save as: static/js/unified-app-core.js (REPLACE existing file)
 * Last Updated: October 28, 2025
 */

function UnifiedTruthLensAnalyzer() {
    console.log('[UnifiedTruthLens] Initializing v6.11.0 with positive messages...');
    
    // Core properties
    this.currentMode = 'news';
    this.isAnalyzing = false;
    this.abortController = null;
    this.MINIMUM_LOADING_TIME = 3000;
    this.progressInterval = null;
    this.messageInterval = null;
    this.factInterval = null;
    this.isYouTubeURL = false;
    
    // Check dependencies
    if (typeof ServiceTemplates === 'undefined') {
        console.error('[UnifiedTruthLens] ServiceTemplates not found!');
    }
    
    console.log('[UnifiedTruthLens] Initialized successfully v6.11.0');
}

// v6.9.0 - CRITICAL FIX: Added startAnalysis method for index.html compatibility
UnifiedTruthLensAnalyzer.prototype.startAnalysis = function(url, text) {
    console.log('[UnifiedTruthLens] startAnalysis called with url:', url ? 'provided' : 'none', 'text:', text ? text.length + ' chars' : 'none');
    
    // Route to the standard analyzeContent method
    this.analyzeContent(url, text, 'news');
};

UnifiedTruthLensAnalyzer.prototype.analyzeContent = function(url, text, mode) {
    console.log('[UnifiedTruthLens] analyzeContent called - mode:', mode, 'url:', url ? 'provided' : 'none', 'text:', text ? text.length + ' chars' : 'none');
    
    if (this.isAnalyzing) {
        console.warn('[UnifiedTruthLens] Analysis already in progress');
        return;
    }
    
    if (!url && !text) {
        alert('Please provide either a URL or text to analyze');
        return;
    }
    
    this.currentMode = mode || 'news';
    this.isAnalyzing = true;
    
    // Check if URL is YouTube
    if (url && (url.includes('youtube.com') || url.includes('youtu.be'))) {
        this.isYouTubeURL = true;
        console.log('[UnifiedTruthLens] YouTube URL detected');
    } else {
        this.isYouTubeURL = false;
    }
    
    this.clearResults();
    this.showLoadingState();
    
    const startTime = Date.now();
    this.abortController = new AbortController();
    
    const endpoint = mode === 'transcript' ? '/api/transcript/analyze' : '/api/analyze';
    const payload = { url: url || '', text: text || '' };
    
    console.log('[UnifiedTruthLens] Sending request to:', endpoint);
    
    fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: this.abortController.signal
    })
    .then(response => {
        console.log('[UnifiedTruthLens] Response status:', response.status);
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || 'Analysis failed');
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('[UnifiedTruthLens] Response data received:', data);
        
        const elapsed = Date.now() - startTime;
        const remainingTime = Math.max(0, this.MINIMUM_LOADING_TIME - elapsed);
        
        setTimeout(() => {
            this.hideLoadingState();
            
            if (data.success || data.data) {
                const analysisData = data.data || data;
                analysisData.analysis_mode = mode;
                this.displayResults(analysisData);
            } else {
                this.showError(data.error || 'Analysis failed');
            }
            
            this.isAnalyzing = false;
        }, remainingTime);
    })
    .catch(error => {
        console.error('[UnifiedTruthLens] Error:', error);
        
        if (error.name === 'AbortError') {
            console.log('[UnifiedTruthLens] Request aborted');
        } else {
            const elapsed = Date.now() - startTime;
            const remainingTime = Math.max(0, this.MINIMUM_LOADING_TIME - elapsed);
            
            setTimeout(() => {
                this.hideLoadingState();
                this.showError(error.message || 'Analysis failed. Please try again.');
                this.isAnalyzing = false;
            }, remainingTime);
        }
    });
};

UnifiedTruthLensAnalyzer.prototype.showLoadingState = function() {
    console.log('[LoadingState] Showing enhanced loading overlay with positive messages');
    
    var loadingBackdrop = document.getElementById('loadingBackdrop');
    var progressContainer = document.getElementById('progressContainerFixed');
    
    if (loadingBackdrop) {
        loadingBackdrop.classList.add('active');
    }
    
    // Animate progress
    this.animateProgress();
    
    // Update messages
    this.updateLoadingMessages();
    
    // Show fun facts
    this.showFunFacts();
};

UnifiedTruthLensAnalyzer.prototype.animateProgress = function() {
    var progressBar = document.getElementById('progressBarFill');
    var progressPercent = document.getElementById('progressPercentageFixed');
    
    if (!progressBar || !progressPercent) return;
    
    var progress = 0;
    var increment = 1;
    
    this.progressInterval = setInterval(() => {
        progress += increment;
        
        if (progress >= 90) {
            clearInterval(this.progressInterval);
            increment = 0.2;
        }
        
        if (progress > 100) progress = 100;
        
        progressBar.style.width = progress + '%';
        progressPercent.textContent = Math.round(progress) + '%';
    }, 100);
};

/**
 * v6.11.0 FIX: POSITIVE, EXCITING PROGRESS MESSAGES
 * Changed from scary "detecting" language to positive "discovering" language
 */
UnifiedTruthLensAnalyzer.prototype.updateLoadingMessages = function() {
    var loadingMessage = document.getElementById('loadingMessageEnhanced');
    if (!loadingMessage) return;
    
    var messages = this.isYouTubeURL ? [
        '🎬 Extracting video transcript...',
        '🔍 Reading through the content...',
        '✨ Discovering key claims and facts...',
        '📚 Checking facts across reliable sources...',
        '👤 Learning about the speaker...',
        '⚡ Evaluating content quality...',
        '🎯 Building your comprehensive report...'
    ] : [
        '📰 Gathering article content...',
        '🛡️ Verifying source reputation...',
        '🎯 Understanding the perspective...',
        '✓ Checking the facts...',
        '👤 Researching the author...',
        '💎 Assessing content quality...',
        '📊 Creating your detailed analysis...'
    ];
    
    var currentIndex = 0;
    
    loadingMessage.textContent = messages[0];
    
    this.messageInterval = setInterval(() => {
        currentIndex = (currentIndex + 1) % messages.length;
        loadingMessage.textContent = messages[currentIndex];
    }, 3000);
};

UnifiedTruthLensAnalyzer.prototype.showFunFacts = function() {
    var funFactBox = document.getElementById('funFact');
    var funFactText = document.getElementById('funFactText');
    
    if (!funFactBox || !funFactText) return;
    
    var facts = [
        '💡 The average person encounters 300-400 pieces of information daily on social media.',
        '🔬 AI can analyze patterns in text that help identify reliable information sources.',
        '📊 Professional news outlets employ editorial standards that include multiple source verification.',
        '🎓 Media literacy education helps people better evaluate information quality.',
        '🌟 Quality journalism involves fact-checking, multiple sources, and editorial oversight.',
        '📖 The first fact-checking organization was created in 1913 by a newspaper editor.',
        '🔍 Cross-referencing claims with multiple sources is a key skill for informed readers.',
        '✨ AI tools can process information faster, but human judgment remains essential.'
    ];
    
    var currentFactIndex = 0;
    funFactText.textContent = facts[0];
    funFactBox.style.display = 'block';
    
    this.factInterval = setInterval(() => {
        currentFactIndex = (currentFactIndex + 1) % facts.length;
        funFactText.textContent = facts[currentFactIndex];
    }, 8000);
};

UnifiedTruthLensAnalyzer.prototype.hideLoadingState = function() {
    console.log('[LoadingState] Hiding loading overlay');
    
    var loadingBackdrop = document.getElementById('loadingBackdrop');
    
    setTimeout(function() {
        if (loadingBackdrop) {
            loadingBackdrop.classList.remove('active');
        }
        
        var analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = analyzeBtn.innerHTML.includes('Transcript') ? 
                '<i class="fas fa-search"></i> Analyze Transcript' : 
                '<i class="fas fa-search"></i> Analyze Article';
        }
    }, 800);
    
    if (this.progressInterval) {
        clearInterval(this.progressInterval);
        this.progressInterval = null;
    }
    if (this.messageInterval) {
        clearInterval(this.messageInterval);
        this.messageInterval = null;
    }
    if (this.factInterval) {
        clearInterval(this.factInterval);
        this.factInterval = null;
    }
    
    // Reset YouTube flag
    this.isYouTubeURL = false;
};

// v6.10.0 - ENHANCED: Now calls updateComprehensiveSummary for new summary section
UnifiedTruthLensAnalyzer.prototype.displayResults = function(data) {
    console.log('[DisplayResults v6.10.0] Displaying results with comprehensive summary');
    
    window.lastAnalysisData = data;
    
    var resultsSection = document.getElementById('resultsSection');
    if (!resultsSection) {
        resultsSection = document.getElementById('results-section');
    }
    if (!resultsSection) {
        console.error('[DisplayResults] Results section not found');
        return;
    }
    
    resultsSection.style.display = 'block';
    
    var modeBadge = document.getElementById('analysisModeBadge');
    if (modeBadge) {
        modeBadge.textContent = data.analysis_mode === 'transcript' ? 'Transcript' : 'News';
    }
    
    // v6.10.0 - NEW: Call comprehensive summary function first (for free tier display)
    if (typeof updateComprehensiveSummary === 'function') {
        console.log('[DisplayResults] Calling updateComprehensiveSummary...');
        updateComprehensiveSummary(data);
    } else {
        console.warn('[DisplayResults] updateComprehensiveSummary function not found');
        // Fallback to old trust display if new function doesn't exist
        if (typeof updateEnhancedTrustDisplay === 'function') {
            console.log('[DisplayResults] Falling back to updateEnhancedTrustDisplay...');
            updateEnhancedTrustDisplay(data);
        }
    }
    
    // Display detailed service results
    var container = document.getElementById('serviceAnalysisContainer') || 
                    document.getElementById('service-results');
    
    if (container && typeof ServiceTemplates !== 'undefined') {
        console.log('[DisplayResults] Displaying service templates...');
        container.innerHTML = '';
        ServiceTemplates.displayAllAnalyses(data, this);
    } else {
        console.error('[DisplayResults] Service container or ServiceTemplates not found');
    }
    
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    console.log('[DisplayResults v6.10.0] Results displayed successfully');
};

UnifiedTruthLensAnalyzer.prototype.clearResults = function() {
    var container = document.getElementById('serviceAnalysisContainer') || 
                    document.getElementById('service-results');
    if (container) container.innerHTML = '';
    
    var resultsSection = document.getElementById('resultsSection') || 
                         document.getElementById('results-section');
    if (resultsSection) resultsSection.style.display = 'none';
    
    // Hide comprehensive summary
    var summaryContainer = document.getElementById('comprehensive-summary');
    if (summaryContainer) summaryContainer.style.display = 'none';
    
    // Hide service wrapper
    var serviceWrapper = document.getElementById('service-results-wrapper');
    if (serviceWrapper) serviceWrapper.style.display = 'none';
    
    window.lastAnalysisData = null;
    
    if (window.ChartRenderer && window.ChartRenderer.destroyAllCharts) {
        window.ChartRenderer.destroyAllCharts();
    }
};

UnifiedTruthLensAnalyzer.prototype.showError = function(message) {
    this.hideLoadingState();
    
    var errorMessage = document.getElementById('errorMessage');
    var errorText = document.getElementById('errorText');
    
    if (errorMessage && errorText) {
        errorText.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.classList.add('active');
        
        setTimeout(function() {
            errorMessage.classList.remove('active');
            setTimeout(function() {
                errorMessage.style.display = 'none';
            }, 300);
        }, 5000);
    } else {
        alert('Error: ' + message);
    }
};

UnifiedTruthLensAnalyzer.prototype.cleanAuthorName = function(author) {
    if (!author || author === 'Unknown' || author === 'N/A') {
        return 'Unknown Author';
    }
    return author.replace(/^by\s+/i, '').trim() || 'Unknown Author';
};

console.log('[UnifiedTruthLens] Loading v6.11.0 - Positive progress messages ready');
var unifiedAnalyzer = new UnifiedTruthLensAnalyzer();

window.UnifiedTruthLensAnalyzer = UnifiedTruthLensAnalyzer;
window.unifiedAnalyzer = unifiedAnalyzer;

/**
 * I did no harm and this file is not truncated.
 */
