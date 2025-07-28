// main.js - News Analyzer Application
// Enhanced with colorful progress animation

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
    
    // Button event listeners
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', analyzeURL);
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
    
    // Enter key support
    if (urlInput) {
        urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                analyzeURL();
            }
        });
    }
    
    // Load history
    loadHistory();
});

// ENHANCED Loading state with colorful animation
function showLoadingState() {
    const loadingDiv = document.getElementById('loading');
    if (loadingDiv) {
        loadingDiv.classList.remove('hidden');
        
        // Replace the simple spinner with a colorful one
        loadingDiv.innerHTML = `
            <div class="progress-container" style="text-align: center; padding: 40px;">
                <div class="rainbow-loader">
                    <div></div>
                    <div></div>
                    <div></div>
                    <div></div>
                    <div></div>
                </div>
                <p style="margin-top: 24px; font-size: 1.125rem; color: #4b5563;">Analyzing article...</p>
                <p style="margin-top: 8px; font-size: 0.875rem; color: #6b7280;">This may take a few moments</p>
            </div>
        `;
    }
}

// Hide loading state
function hideLoadingState() {
    const loadingDiv = document.getElementById('loading');
    if (loadingDiv) {
        loadingDiv.classList.add('hidden');
    }
}

// Show error message
function showError(message) {
    // Hide loading first
    hideLoadingState();
    
    // Create error element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = `
        background-color: #fee2e2;
        border: 1px solid #fca5a5;
        color: #991b1b;
        padding: 16px;
        border-radius: 8px;
        margin: 16px 0;
        text-align: center;
    `;
    errorDiv.textContent = message;
    
    // Insert after the analyzer card
    const analyzerCard = document.querySelector('.analyzer-card');
    if (analyzerCard && analyzerCard.parentNode) {
        // Remove any existing error
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        analyzerCard.parentNode.insertBefore(errorDiv, analyzerCard.nextSibling);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorDiv.style.opacity = '0';
            errorDiv.style.transition = 'opacity 0.3s ease';
            setTimeout(() => errorDiv.remove(), 300);
        }, 5000);
    }
}

// Analyze URL function
async function analyzeURL() {
    const urlInput = document.getElementById('urlInput');
    const url = urlInput ? urlInput.value.trim() : '';
    
    if (!url) {
        showError('Please enter a URL');
        return;
    }
    
    // Basic URL validation
    try {
        new URL(url);
    } catch (e) {
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
        
        console.log('Starting analysis for URL:', url);
        
        // Store current URL for refresh
        if (window.UI) {
            window.UI.currentUrl = url;
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
        
        // Display results
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
        
        // Display results
        displayResults(result);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'An error occurred during analysis');
    } finally {
        analysisInProgress = false;
        hideLoadingState();
    }
}

// Display analysis results
function displayResults(result) {
    console.log('=== DISPLAYING RESULTS ===');
    console.log('Full result object:', result);
    
    // Store globally for debugging
    window.LAST_ANALYSIS_DATA = result;
    
    // Show results section
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.classList.remove('hidden');
    }
    
    // Display author analysis with enhanced debugging
    console.log('=== AUTHOR ANALYSIS DATA ===');
    console.log('Author analysis exists:', !!result.author_analysis);
    console.log('Author analysis object:', result.author_analysis);
    
    if (result.author_analysis) {
        console.log('Author name:', result.author_analysis.name);
        console.log('Author found:', result.author_analysis.found);
        console.log('Author credibility score:', result.author_analysis.credibility_score);
        console.log('Author bio:', result.author_analysis.bio);
        console.log('Full author data:', JSON.stringify(result.author_analysis, null, 2));
    }
    
    // Use UI controller to build results
    if (window.UI && typeof window.UI.buildResults === 'function') {
        console.log('Using UI.buildResults to display results');
        try {
            window.UI.buildResults(result);
            
            // Verify if author card was actually rendered with better timing
            // Use requestAnimationFrame to ensure DOM has been painted
            requestAnimationFrame(() => {
                // Then use setTimeout to give any remaining async operations time to complete
                setTimeout(() => {
                    const authorCard = document.querySelector('[data-card-type="author"]');
                    if (authorCard) {
                        console.log('Author card found in DOM:', authorCard);
                        console.log('Author card HTML preview:', authorCard.innerHTML.substring(0, 200) + '...');
                    } else {
                        console.log('WARNING: Author card not found in DOM after UI.buildResults');
                        
                        // Additional debugging - check what IS in the DOM
                        const allCards = document.querySelectorAll('[data-card-type]');
                        console.log('Total cards found:', allCards.length);
                        allCards.forEach((card, index) => {
                            console.log(`Card ${index + 1}:`, card.getAttribute('data-card-type'));
                        });
                        
                        // Check if cards-grid-wrapper exists
                        const gridWrapper = document.querySelector('.cards-grid-wrapper');
                        console.log('Grid wrapper found:', !!gridWrapper);
                        if (gridWrapper) {
                            console.log('Grid wrapper children:', gridWrapper.children.length);
                        }
                    }
                }, 250); // Increased timeout
            });
        } catch (error) {
            console.error('Error in UI.buildResults:', error);
            displayResultsFallback(result);
        }
    } else {
        console.log('UI controller not available, using fallback display');
        displayResultsFallback(result);
    }
}

// Fallback results display
function displayResultsFallback(result) {
    const resultsDiv = document.getElementById('results');
    if (!resultsDiv) return;
    
    let html = '<div class="results-content">';
    
    // Article info
    if (result.article) {
        html += `
            <div class="article-info">
                <h3>${result.article.title || 'Untitled Article'}</h3>
                <p>By ${result.article.author || 'Unknown Author'}</p>
            </div>
        `;
    }
    
    // Overall credibility
    if (result.overall_credibility !== undefined) {
        html += `
            <div class="credibility-score">
                <h4>Overall Credibility: ${Math.round(result.overall_credibility)}/100</h4>
            </div>
        `;
    }
    
    // Author analysis
    if (result.author_analysis) {
        html += `
            <div class="author-analysis">
                <h4>Author Analysis</h4>
                <p><strong>Name:</strong> ${result.author_analysis.name}</p>
                <p><strong>Found:</strong> ${result.author_analysis.found ? 'Yes' : 'No'}</p>
                <p><strong>Credibility:</strong> ${result.author_analysis.credibility_score}/100</p>
                ${result.author_analysis.bio ? `<p><strong>Bio:</strong> ${result.author_analysis.bio}</p>` : ''}
            </div>
        `;
    }
    
    html += '</div>';
    resultsDiv.innerHTML = html;
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
        resultsDiv.classList.add('hidden');
        resultsDiv.innerHTML = '';
    }
    
    // Remove any error messages
    const errorMessages = document.querySelectorAll('.error-message');
    errorMessages.forEach(msg => msg.remove());
    
    // Clear global data
    currentArticleData = null;
    
    // Remove analysis cards
    document.querySelectorAll('.analysis-card-standalone, .cards-grid-wrapper, .detailed-analysis-container').forEach(el => el.remove());
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
        
        // Refresh history display
        loadHistory();
    } catch (e) {
        console.error('Error saving to history:', e);
    }
}

// Load history
function loadHistory() {
    try {
        const history = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
        // Could display this in a sidebar or dropdown
        console.log('Analysis history:', history);
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
        // Use the UI controller's PDF export
        if (window.UI && window.UI.exportPDF) {
            window.UI.exportPDF(currentArticleData);
        } else {
            showError('PDF export not available');
        }
    } else if (format === 'json') {
        // Download as JSON
        const dataStr = JSON.stringify(currentArticleData, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportName = `analysis_${new Date().toISOString().split('T')[0]}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportName);
        linkElement.click();
    }
};

// Add the CSS for the rainbow loader
if (!document.querySelector('style[data-component="rainbow-loader"]')) {
    const style = document.createElement('style');
    style.setAttribute('data-component', 'rainbow-loader');
    style.textContent = `
        .rainbow-loader {
            display: inline-flex;
            gap: 4px;
        }
        
        .rainbow-loader div {
            width: 16px;
            height: 60px;
            border-radius: 8px;
            animation: rainbow-dance 1.5s ease-in-out infinite;
        }
        
        .rainbow-loader div:nth-child(1) {
            background: #ff6b6b;
            animation-delay: 0s;
        }
        
        .rainbow-loader div:nth-child(2) {
            background: #4ecdc4;
            animation-delay: 0.1s;
        }
        
        .rainbow-loader div:nth-child(3) {
            background: #45b7d1;
            animation-delay: 0.2s;
        }
        
        .rainbow-loader div:nth-child(4) {
            background: #f9ca24;
            animation-delay: 0.3s;
        }
        
        .rainbow-loader div:nth-child(5) {
            background: #f85f73;
            animation-delay: 0.4s;
        }
        
        @keyframes rainbow-dance {
            0%, 40%, 100% {
                transform: scaleY(0.4) translateY(0);
            }
            20% {
                transform: scaleY(1) translateY(-20px);
            }
        }
        
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
                transform: scale(1);
            }
            50% {
                opacity: 0.9;
                transform: scale(0.98);
            }
        }
        
        @keyframes fadeOut {
            to {
                opacity: 0;
                transform: translateY(-10px);
            }
        }
    `;
    document.head.appendChild(style);
}
