// static/js/main.js
// Main application JavaScript

// Global state
let currentArticleData = null;
let analysisInProgress = false;

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('News Analyzer initialized');
    
    // Get DOM elements
    const urlInput = document.getElementById('urlInput');
    const textInput = document.getElementById('textInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const analyzeTextBtn = document.getElementById('analyzeTextBtn');
    const resetBtn = document.getElementById('resetBtn');
    const resetTextBtn = document.getElementById('resetTextBtn');
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    // Tab switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            
            // Update active states
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Show/hide appropriate input groups
            const urlGroup = document.getElementById('urlInputGroup');
            const textGroup = document.getElementById('textInputGroup');
            
            if (tab === 'url') {
                urlGroup.classList.remove('hidden');
                textGroup.classList.add('hidden');
            } else {
                urlGroup.classList.add('hidden');
                textGroup.classList.remove('hidden');
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
                        <span>Generating Report</span>
                    </div>
                </div>
                <div class="progress-status">Starting analysis...</div>
            </div>
        `;
        
        progressContainer.classList.remove('hidden');
        
        // Animate progress steps
        let currentStep = 0;
        const steps = ['extract', 'analyze', 'verify', 'complete'];
        const messages = [
            'Extracting article content...',
            'Analyzing bias and credibility...',
            'Checking facts and sources...',
            'Generating comprehensive report...'
        ];
        
        const interval = setInterval(() => {
            if (currentStep < steps.length) {
                // Update active step
                progressContainer.querySelectorAll('.progress-step').forEach((step, index) => {
                    if (index <= currentStep) {
                        step.classList.add('active');
                    }
                });
                
                // Update progress bar
                const progressFill = progressContainer.querySelector('.progress-fill');
                if (progressFill) {
                    progressFill.style.width = `${((currentStep + 1) / steps.length) * 100}%`;
                }
                
                // Update status message
                const statusDiv = progressContainer.querySelector('.progress-status');
                if (statusDiv && messages[currentStep]) {
                    statusDiv.textContent = messages[currentStep];
                }
                
                currentStep++;
            }
        }, 800);
        
        // Store interval for cleanup
        progressContainer.dataset.interval = interval;
    }
    
    // Also show the simple loading spinner as fallback
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
        console.log('Text analysis complete:', result);
        
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

// Transform API data to match UI component expectations
function transformApiData(result) {
    if (!result) return result;
    
    // Fix fact_checks structure (should be an array for UI components)
    if (result.fact_checks && !Array.isArray(result.fact_checks)) {
        result.fact_checks = result.fact_checks.claims || [];
    }
    
    // Transform author_analysis to author_info (what AuthorCard expects)
    if (result.author_analysis && !result.author_info) {
        result.author_info = result.author_analysis;
    }
    
    // Ensure key_claims is an array
    if (result.key_claims && !Array.isArray(result.key_claims)) {
        result.key_claims = [];
    }
    
    // Ensure success field exists
    result.success = true;
    
    // Add any missing expected fields with defaults
    result.bias_score = result.bias_analysis?.bias_score || 0;
    result.overall_bias = result.bias_analysis?.overall_bias || 'Unknown';
    
    return result;
}

// Display analysis results using the enhanced UI controller
function displayResults(result) {
    console.log('=== DISPLAYING RESULTS ===');
    console.log('Full result object:', result);
    
    // Transform data to match UI expectations
    result = transformApiData(result);
    
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
    
    // Hide results
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.innerHTML = '';
        resultsDiv.classList.add('hidden');
    }
    
    // Hide enhanced analysis
    const enhancedAnalysis = document.getElementById('enhancedAnalysis');
    if (enhancedAnalysis) {
        enhancedAnalysis.classList.add('hidden');
    }
    
    // Reset analyzer card
    const analyzerCard = document.querySelector('.analyzer-card');
    if (analyzerCard) {
        analyzerCard.classList.remove('analyzer-card-minimized');
    }
    
    // Clear stored data
    currentArticleData = null;
    analysisInProgress = false;
    
    // Clear UI controller state
    if (window.UI) {
        window.UI.clearResults();
        window.UI.currentURL = null;
        window.UI.currentText = null;
    }
    
    console.log('Analysis reset');
}

// Save to history
function saveToHistory(url, data) {
    try {
        const history = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
        
        history.unshift({
            url: url,
            title: data.article?.title || 'Unknown',
            trustScore: data.trust_score || 0,
            date: new Date().toISOString()
        });
        
        // Keep only last 10 items
        history.splice(10);
        
        localStorage.setItem('analysisHistory', JSON.stringify(history));
    } catch (e) {
        console.error('Error saving to history:', e);
    }
}

// Load history
function loadHistory() {
    try {
        const history = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
        
        if (history.length === 0) return;
        
        console.log('Loaded analysis history:', history.length, 'items');
        
        // Could display history in UI if needed
    } catch (e) {
        console.error('Error loading history:', e);
    }
}

// Export functions for debugging
window.analyzeURL = analyzeURL;
window.analyzeText = analyzeText;
window.resetAnalysis = resetAnalysis;
window.displayResults = displayResults;
window.transformApiData = transformApiData;

// Add CSS for progress bar
const style = document.createElement('style');
style.textContent = `
    .progress-bar-wrapper {
        margin: 20px 0;
        padding: 20px;
        background: #f9fafb;
        border-radius: 12px;
    }
    
    .progress-bar {
        height: 8px;
        background: #e5e7eb;
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 20px;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(to right, #3b82f6, #6366f1);
        border-radius: 4px;
        width: 0%;
        transition: width 0.8s ease-out;
    }
    
    .progress-steps {
        display: flex;
        justify-content: space-between;
        margin-bottom: 15px;
    }
    
    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        opacity: 0.4;
        transition: opacity 0.3s;
    }
    
    .progress-step.active {
        opacity: 1;
    }
    
    .step-icon {
        font-size: 24px;
    }
    
    .progress-step span:not(.step-icon) {
        font-size: 12px;
        color: #6b7280;
        text-align: center;
    }
    
    .progress-status {
        text-align: center;
        color: #374151;
        font-weight: 500;
    }
    
    .error-card {
        background: white;
        border: 2px solid #fee2e2;
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        max-width: 500px;
        margin: 40px auto;
    }
    
    .error-icon {
        font-size: 48px;
        margin-bottom: 15px;
    }
    
    .error-card h3 {
        color: #991b1b;
        margin-bottom: 10px;
    }
    
    .error-card p {
        color: #374151;
        margin-bottom: 20px;
    }
    
    .results-fallback {
        background: white;
        border-radius: 12px;
        padding: 30px;
        max-width: 600px;
        margin: 40px auto;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .basic-results {
        margin: 20px 0;
        padding: 20px;
        background: #f9fafb;
        border-radius: 8px;
    }
    
    .basic-results p {
        margin: 10px 0;
        font-size: 16px;
    }
    
    .upgrade-notice {
        color: #6b7280;
        font-style: italic;
        text-align: center;
        margin-top: 20px;
    }
`;
document.head.appendChild(style);

console.log('Main.js loaded successfully');
