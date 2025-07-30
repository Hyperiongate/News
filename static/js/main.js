// main.js - News Analyzer Application
// Enhanced with support for new components

// Global state
let currentArticleData = null;
let analysisInProgress = false;

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('News Analyzer initialized');
    
    // Get DOM elements
    const urlInput = document.getElementById('urlInput');
    const textInput = document.getElementById('textInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const analyzeTextBtn = document.getElementById('analyzeTextBtn');
    const resetBtn = document.getElementById('resetBtn');
    const resetTextBtn = document.getElementById('resetTextBtn');
    
    // Tab functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    const urlInputGroup = document.getElementById('urlInputGroup');
    const textInputGroup = document.getElementById('textInputGroup');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            
            // Update active tab
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Show appropriate input
            if (tab === 'url') {
                urlInputGroup.classList.remove('hidden');
                textInputGroup.classList.add('hidden');
            } else {
                urlInputGroup.classList.add('hidden');
                textInputGroup.classList.remove('hidden');
            }
        });
    });
    
    // Event listeners
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', analyzeURL);
        // Enter key support
        if (urlInput) {
            urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') analyzeURL();
            });
        }
    }
    
    if (analyzeTextBtn) {
        analyzeTextBtn.addEventListener('click', analyzeText);
    }
    
    if (resetBtn) {
        resetBtn.addEventListener('click', resetAnalysis);
    }
    
    if (resetTextBtn) {
        resetTextBtn.addEventListener('click', resetAnalysis);
    }
    
    // Load history on startup
    loadHistory();
});

// Show loading state with enhanced animation
function showLoadingState() {
    console.log('Showing loading state');
    const progressContainer = document.getElementById('progressContainer');
    
    if (progressContainer) {
        progressContainer.innerHTML = `
            <div class="progress-bar-wrapper">
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
                <div class="progress-steps">
                    <div class="progress-step active" data-step="extract">
                        <span class="step-icon">📄</span>
                        <span>Extracting Content</span>
                    </div>
                    <div class="progress-step" data-step="analyze">
                        <span class="step-icon">🔍</span>
                        <span>Analyzing Article</span>
                    </div>
                    <div class="progress-step" data-step="verify">
                        <span class="step-icon">✓</span>
                        <span>Verifying Facts</span>
                    </div>
                    <div class="progress-step" data-step="complete">
                        <span class="step-icon">📊</span>
                        <span>Preparing Results</span>
                    </div>
                </div>
            </div>
        `;
        progressContainer.classList.remove('hidden');
        
        // Animate progress steps
        let currentStep = 0;
        const steps = ['extract', 'analyze', 'verify', 'complete'];
        const stepInterval = setInterval(() => {
            if (currentStep < steps.length) {
                document.querySelectorAll('.progress-step').forEach((step, index) => {
                    if (index <= currentStep) {
                        step.classList.add('active');
                    }
                });
                currentStep++;
            } else {
                clearInterval(stepInterval);
            }
        }, 1000);
        
        // Store interval for cleanup
        progressContainer.dataset.interval = stepInterval;
    }
    
    // Also show fallback loading
    const loadingDiv = document.getElementById('loading');
    if (loadingDiv) {
        loadingDiv.classList.remove('hidden');
    }
}

// Hide loading state
function hideLoadingState() {
    console.log('Hiding loading state');
    
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        // Clear interval if exists
        const interval = progressContainer.dataset.interval;
        if (interval) {
            clearInterval(interval);
        }
        progressContainer.innerHTML = '';
        progressContainer.classList.add('hidden');
    }
    
    const loadingDiv = document.getElementById('loading');
    if (loadingDiv) {
        loadingDiv.classList.add('hidden');
    }
}

// Show error message
function showError(message) {
    console.error('Error:', message);
    
    // Hide loading states
    hideLoadingState();
    
    // Show error in results area
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.innerHTML = `
            <div class="error-card">
                <div class="error-icon">❌</div>
                <h3>Analysis Error</h3>
                <p>${message}</p>
                <button class="btn btn-secondary" onclick="resetAnalysis()">Try Again</button>
            </div>
        `;
        resultsDiv.classList.remove('hidden');
    }
    
    // Also use UI controller error if available
    if (window.UI && window.UI.showError) {
        window.UI.showError(message);
    }
}

// Analyze URL function
async function analyzeURL() {
    const urlInput = document.getElementById('urlInput');
    const url = urlInput ? urlInput.value.trim() : '';
    
    if (!url) {
        showError('Please enter a valid URL');
        return;
    }
    
    if (analysisInProgress) {
        showError('Analysis already in progress. Please wait...');
        return;
    }
    
    try {
        analysisInProgress = true;
        showLoadingState();
        
        console.log('Starting URL analysis:', url);
        
        // Store current URL for refresh
        if (window.UI) {
            window.UI.currentURL = url;
        }
        
        // Call the API
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Analysis complete:', result);
        
        // Store the result
        currentArticleData = result;
        
        // Display results using enhanced UI controller
        displayResults(result);
        
        // Save to history
        saveToHistory(url, result);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'An error occurred during analysis');
    } finally {
        analysisInProgress = false;
        hideLoadingState();
    }
}

// Analyze text function
async function analyzeText() {
    const textInput = document.getElementById('textInput');
    const text = textInput ? textInput.value.trim() : '';
    
    if (!text) {
        showError('Please enter some text to analyze');
        return;
    }
    
    if (analysisInProgress) {
        showError('Analysis already in progress. Please wait...');
        return;
    }
    
    try {
        analysisInProgress = true;
        showLoadingState();
        
        console.log('Starting text analysis...');
        
        // Store current text for refresh
        if (window.UI) {
            window.UI.currentText = text;
        }
        
        // Call the API with text
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Analysis complete:', result);
        
        // Store the result
        currentArticleData = result;
        
        // Display results using enhanced UI controller
        displayResults(result);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'An error occurred during analysis');
    } finally {
        analysisInProgress = false;
        hideLoadingState();
    }
}

// Display analysis results using the enhanced UI controller
function displayResults(result) {
    console.log('=== DISPLAYING RESULTS ===');
    console.log('Full result object:', result);
    
    // Store globally for debugging
    window.LAST_ANALYSIS_DATA = result;
    
    // Clear any existing results
    if (window.UI && window.UI.clearResults) {
        window.UI.clearResults();
    }
    
    // Use the enhanced UI controller to render results
    if (window.UI && window.UI.renderResults) {
        console.log('Using enhanced UI controller to render results');
        window.UI.renderResults(result);
    } else {
        console.error('UI controller not available');
        // Fallback to basic display
        displayResultsFallback(result);
    }
    
    // Ensure the enhanced analysis section is visible
    const enhancedAnalysis = document.getElementById('enhancedAnalysis');
    if (enhancedAnalysis && result) {
        enhancedAnalysis.classList.remove('hidden');
    }
}

// Fallback results display (in case UI controller fails)
function displayResultsFallback(result) {
    const resultsDiv = document.getElementById('results');
    if (!resultsDiv) return;
    
    resultsDiv.innerHTML = `
        <div class="results-fallback">
            <h2>Analysis Complete</h2>
            <div class="basic-results">
                <p><strong>Trust Score:</strong> ${result.trust_score || 'N/A'}/100</p>
                <p><strong>Source:</strong> ${result.article?.domain || 'Unknown'}</p>
                <p><strong>Author:</strong> ${result.article?.author || 'Unknown'}</p>
                <p><strong>Bias:</strong> ${result.bias_analysis?.overall_bias || 'Unknown'}</p>
            </div>
            <p class="upgrade-notice">
                Enable JavaScript and refresh the page for full enhanced analysis.
            </p>
        </div>
    `;
    resultsDiv.classList.remove('hidden');
}

// Reset analysis
function resetAnalysis() {
    // Clear inputs
    const urlInput = document.getElementById('urlInput');
    const textInput = document.getElementById('textInput');
    if (urlInput) urlInput.value = '';
    if (textInput) textInput.value = '';
    
    // Clear results using UI controller
    if (window.UI && window.UI.clearResults) {
        window.UI.clearResults();
    }
    
    // Also manually hide results sections
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.classList.add('hidden');
        resultsDiv.innerHTML = '';
    }
    
    const enhancedDiv = document.getElementById('enhancedAnalysis');
    if (enhancedDiv) {
        enhancedDiv.classList.add('hidden');
    }
    
    // Remove any error messages
    const errorMessages = document.querySelectorAll('.error-message, .error-card');
    errorMessages.forEach(msg => msg.remove());
    
    // Clear global data
    currentArticleData = null;
    
    // Clear progress
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.innerHTML = '';
        progressContainer.classList.add('hidden');
    }
}

// Save to history
function saveToHistory(url, data) {
    try {
        let history = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
        
        // Add new entry
        history.unshift({
            url: url,
            title: data.article?.title || 'Untitled',
            date: new Date().toISOString(),
            trustScore: data.trust_score || 0
        });
        
        // Keep only last 10
        history = history.slice(0, 10);
        
        localStorage.setItem('analysisHistory', JSON.stringify(history));
        
        console.log('Saved to history');
    } catch (e) {
        console.error('Error saving to history:', e);
    }
}

// Load history
function loadHistory() {
    try {
        const history = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
        console.log('Loaded history:', history.length, 'items');
        // Could display this in a sidebar or dropdown
    } catch (e) {
        console.error('Error loading history:', e);
    }
}

// Export functionality
window.exportAnalysis = function(format) {
    if (!currentArticleData) {
        showError('No analysis data to export');
        return;
    }
    
    if (format === 'pdf') {
        // Use the export handler component if available
        if (window.UI && window.UI.components.exportHandler) {
            window.UI.components.exportHandler.exportPDF(currentArticleData);
        } else {
            showError('PDF export not available');
        }
    } else if (format === 'json') {
        // Download as JSON
        const dataStr = JSON.stringify(currentArticleData, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportName = `news-analysis_${new Date().toISOString().split('T')[0]}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportName);
        linkElement.click();
    }
};

// Refresh analysis
window.refreshAnalysis = function() {
    if (window.UI) {
        if (window.UI.currentURL) {
            const urlInput = document.getElementById('urlInput');
            if (urlInput) {
                urlInput.value = window.UI.currentURL;
                analyzeURL();
            }
        } else if (window.UI.currentText) {
            const textInput = document.getElementById('textInput');
            if (textInput) {
                textInput.value = window.UI.currentText;
                analyzeText();
            }
        }
    }
};

// Utility function to check if enhanced components are loaded
function checkEnhancedComponents() {
    const components = {
        TrustScore: !!window.TrustScore,
        BiasAnalysis: !!window.BiasAnalysis,
        FactChecker: !!window.FactChecker,
        AuthorCard: !!window.AuthorCard,
        ClickbaitDetector: !!window.ClickbaitDetector,
        SourceCredibility: !!window.SourceCredibility,
        ManipulationDetector: !!window.ManipulationDetector,
        TransparencyAnalysis: !!window.TransparencyAnalysis
    };
    
    console.log('Enhanced components status:', components);
    return components;
}

// Check components after a delay
setTimeout(checkEnhancedComponents, 2000);

// Add progress bar styles if not already present
if (!document.querySelector('style[data-component="progress-styles"]')) {
    const style = document.createElement('style');
    style.setAttribute('data-component', 'progress-styles');
    style.textContent = `
        .progress-bar-wrapper {
            margin: 20px 0;
        }
        
        .progress-bar {
            height: 4px;
            background: #e5e7eb;
            border-radius: 2px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3b82f6, #6366f1);
            width: 0;
            animation: progressAnimation 4s ease-out forwards;
        }
        
        @keyframes progressAnimation {
            to { width: 100%; }
        }
        
        .progress-steps {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .progress-step {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            opacity: 0.3;
            transition: opacity 0.3s ease;
        }
        
        .progress-step.active {
            opacity: 1;
        }
        
        .step-icon {
            font-size: 24px;
        }
        
        .progress-step span:last-child {
            font-size: 12px;
            color: #6b7280;
        }
        
        .error-card {
            background: white;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            margin: 40px auto;
        }
        
        .error-icon {
            font-size: 48px;
            margin-bottom: 20px;
        }
        
        .error-card h3 {
            color: #ef4444;
            margin-bottom: 10px;
        }
        
        .error-card p {
            color: #6b7280;
            margin-bottom: 20px;
        }
    `;
    document.head.appendChild(style);
}
