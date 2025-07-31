// main.js - Complete News Analyzer Application
// Updated to work with YOUR file structure

// Global state
let currentAnalysis = null;
let analysisInProgress = false;

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Set up event listeners
    setupEventListeners();
    
    // Initialize with sample URL if in development
    if (window.location.hostname === 'localhost') {
        document.getElementById('url-input').value = 'https://www.example.com/article';
    }
}

// Set up all event listeners
function setupEventListeners() {
    // Analyze button
    const analyzeBtn = document.getElementById('analyze-btn');
    const urlInput = document.getElementById('url-input');
    
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', handleAnalyze);
    }
    
    // Enter key in URL input
    if (urlInput) {
        urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleAnalyze();
            }
        });
    }
}

// Handle analyze button click
async function handleAnalyze() {
    const urlInput = document.getElementById('url-input');
    const url = urlInput.value.trim();
    
    if (!url) {
        showError('Please enter a URL to analyze');
        return;
    }
    
    if (!isValidUrl(url)) {
        showError('Please enter a valid URL');
        return;
    }
    
    if (analysisInProgress) {
        showError('Analysis already in progress');
        return;
    }
    
    await analyzeArticle(url);
}

// Validate URL
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

// Main analysis function with progress animation
async function analyzeArticle(url) {
    analysisInProgress = true;
    
    const resultsSection = document.getElementById('results-section');
    const progressBar = document.querySelector('.progress-bar');
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');
    const analyzeBtn = document.getElementById('analyze-btn');
    
    // Hide previous results and errors
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
    hideError();
    
    // Disable analyze button
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = 'Analyzing...';
    }
    
    // Show and animate progress bar
    if (progressBar) {
        progressBar.style.display = 'block';
        progressFill.style.width = '0%';
        progressText.textContent = 'Starting analysis...';
    }
    
    let progress = 0;
    const progressSteps = [
        { percent: 10, text: 'Fetching article...' },
        { percent: 25, text: 'Analyzing bias...' },
        { percent: 40, text: 'Fact-checking claims...' },
        { percent: 55, text: 'Evaluating transparency...' },
        { percent: 70, text: 'Researching author...' },
        { percent: 85, text: 'Analyzing context...' },
        { percent: 95, text: 'Finalizing results...' }
    ];
    
    let stepIndex = 0;
    const progressInterval = setInterval(() => {
        if (stepIndex < progressSteps.length) {
            const step = progressSteps[stepIndex];
            progress = step.percent;
            if (progressFill) progressFill.style.width = `${progress}%`;
            if (progressText) progressText.textContent = step.text;
            stepIndex++;
        }
    }, 400);
    
    try {
        // Make API call
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Clear progress interval
        clearInterval(progressInterval);
        
        // Complete progress animation
        if (progressFill) progressFill.style.width = '100%';
        if (progressText) progressText.textContent = 'Analysis complete!';
        
        // Transform and store results
        currentAnalysis = transformApiData(result);
        
        // Wait briefly then show results
        setTimeout(() => {
            if (progressBar) progressBar.style.display = 'none';
            displayResults(currentAnalysis);
            if (resultsSection) resultsSection.style.display = 'block';
        }, 500);
        
    } catch (error) {
        clearInterval(progressInterval);
        console.error('Analysis error:', error);
        showError('Failed to analyze article. Please try again.');
        
        if (progressBar) progressBar.style.display = 'none';
    } finally {
        analysisInProgress = false;
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Analyze Article';
        }
    }
}

// Transform API data to match UI expectations
function transformApiData(result) {
    if (!result) return result;
    
    // Fix fact_checks structure
    if (result.fact_checks && !Array.isArray(result.fact_checks)) {
        result.fact_checks = result.fact_checks.claims || [];
    }
    
    // Transform author_analysis to author_info
    if (result.author_analysis && !result.author_info) {
        result.author_info = result.author_analysis;
    }
    
    // DEVELOPMENT MODE: Force all features to be unlocked
    result.is_pro = true;
    
    // Ensure all required fields exist
    result.success = true;
    result.article = result.article || {};
    result.bias_analysis = result.bias_analysis || {};
    result.transparency_analysis = result.transparency_analysis || {};
    result.context_analysis = result.context_analysis || {};
    result.readability_analysis = result.readability_analysis || {};
    result.emotional_tone_analysis = result.emotional_tone_analysis || {};
    result.comparison_analysis = result.comparison_analysis || {};
    
    return result;
}

// Display all analysis results
function displayResults(data) {
    if (!data || !data.success) {
        showError('No results to display');
        return;
    }
    
    const container = document.querySelector('.results-grid');
    if (!container) {
        console.error('Results grid container not found');
        return;
    }
    
    // Clear previous results
    container.innerHTML = '';
    
    // Define all cards using YOUR component names from file structure
    const cards = [
        { component: window.BiasAnalysis, name: 'BiasAnalysis' },
        { component: window.FactChecker, name: 'FactChecker' },
        { component: window.TransparencyAnalysis, name: 'TransparencyAnalysis' },
        { component: window.AuthorCard, name: 'AuthorCard' },
        { component: window.ContextCard, name: 'ContextCard' },
        { component: window.ReadabilityCard, name: 'ReadabilityCard' },
        { component: window.EmotionalToneCard, name: 'EmotionalToneCard' },
        { component: window.ComparisonCard, name: 'ComparisonCard' }
    ];
    
    // Render all cards
    cards.forEach(({ component, name }) => {
        if (!component) {
            console.warn(`${name} component not found - check if file exists and exports class correctly`);
            return;
        }
        
        try {
            const cardInstance = new component();
            const element = cardInstance.render(data);
            if (element) {
                container.appendChild(element);
            }
        } catch (error) {
            console.error(`Error rendering ${name}:`, error);
        }
    });
    
    // Initialize dropdowns after cards are rendered
    setTimeout(initializeDropdowns, 100);
}

// Initialize dropdown functionality for all cards
function initializeDropdowns() {
    // Add click handlers to all analysis headers
    document.querySelectorAll('.analysis-header').forEach(header => {
        // Skip if already initialized
        if (header.dataset.dropdownInit) return;
        header.dataset.dropdownInit = 'true';
        
        header.style.cursor = 'pointer';
        
        // Add dropdown arrow if not present
        if (!header.querySelector('.dropdown-arrow')) {
            const arrow = document.createElement('span');
            arrow.className = 'dropdown-arrow';
            arrow.innerHTML = '▼';
            arrow.style.marginLeft = 'auto';
            arrow.style.transition = 'transform 0.3s';
            header.appendChild(arrow);
        }
        
        header.addEventListener('click', function(e) {
            // Prevent event bubbling
            e.stopPropagation();
            
            const card = this.closest('.analysis-card');
            if (!card) return;
            
            // Find the content section (try ALL possible class names)
            const contentSelectors = [
                '.card-content',
                '.bias-content',
                '.fact-check-content',
                '.transparency-content',
                '.author-content',
                '.context-content',
                '.readability-content',
                '.emotional-content',
                '.comparison-content',
                '.bias-analysis-content',      // For bias-analysis.js
                '.fact-checker-content',        // For fact-checker.js
                '.transparency-analysis-content' // For transparency-analysis.js
            ];
            
            let content = null;
            for (const selector of contentSelectors) {
                content = card.querySelector(selector);
                if (content) break;
            }
            
            const arrow = this.querySelector('.dropdown-arrow');
            
            if (content) {
                // Toggle expanded state
                const isExpanded = content.style.display === 'block';
                content.style.display = isExpanded ? 'none' : 'block';
                if (arrow) {
                    arrow.style.transform = isExpanded ? 'rotate(0deg)' : 'rotate(180deg)';
                }
                
                // Add/remove expanded class
                card.classList.toggle('expanded', !isExpanded);
            } else {
                console.warn('No content section found for card:', card);
            }
        });
        
        // Start with first two cards expanded
        const allHeaders = document.querySelectorAll('.analysis-header');
        const index = Array.from(allHeaders).indexOf(header);
        if (index < 2) {
            header.click();
        }
    });
}

// Show error message
function showError(message) {
    const errorEl = document.getElementById('error-message');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
        
        // Hide after 5 seconds
        setTimeout(() => {
            errorEl.style.display = 'none';
        }, 5000);
    }
}

// Hide error message
function hideError() {
    const errorEl = document.getElementById('error-message');
    if (errorEl) {
        errorEl.style.display = 'none';
    }
}

// Export for debugging
window.debugAnalysis = {
    getCurrentData: () => currentAnalysis,
    rerunDisplay: () => displayResults(currentAnalysis),
    testProgress: () => analyzeArticle('https://test.com'),
    checkComponents: () => {
        const components = {
            'BiasAnalysis': window.BiasAnalysis,
            'FactChecker': window.FactChecker,
            'TransparencyAnalysis': window.TransparencyAnalysis,
            'AuthorCard': window.AuthorCard,
            'ComparisonCard': window.ComparisonCard,
            'ContextCard': window.ContextCard,
            'EmotionalToneCard': window.EmotionalToneCard,
            'ReadabilityCard': window.ReadabilityCard
        };
        
        console.log('Component Status:');
        Object.entries(components).forEach(([name, component]) => {
            console.log(`${name}: ${component ? '✓ Loaded' : '✗ Missing'}`);
        });
    }
};
