// main.js - Complete News Analyzer Application

// Global state
let currentAnalysis = null;
let analysisInProgress = false;

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Add card styles
    addCardStyles();
    
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
    
    // Settings toggle
    const settingsToggle = document.querySelector('.settings-toggle');
    if (settingsToggle) {
        settingsToggle.addEventListener('click', toggleSettings);
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
    
    // Hide previous results
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
    
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
    
    // Define all 8 cards that should be displayed
    const cards = [
        { component: window.BiasCard, name: 'BiasCard' },
        { component: window.FactCheckCard, name: 'FactCheckCard' },
        { component: window.TransparencyCard, name: 'TransparencyCard' },
        { component: window.AuthorCard, name: 'AuthorCard' },
        { component: window.ContextCard, name: 'ContextCard' },
        { component: window.ReadabilityCard, name: 'ReadabilityCard' },
        { component: window.EmotionalToneCard, name: 'EmotionalToneCard' },
        { component: window.ComparisonCard, name: 'ComparisonCard' }
    ];
    
    // Render all cards
    cards.forEach(({ component, name }) => {
        if (!component) {
            console.warn(`${name} component not found`);
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
            
            // Find the content section (try multiple class names)
            const contentSelectors = [
                '.card-content',
                '.bias-content',
                '.fact-check-content',
                '.transparency-content',
                '.author-content',
                '.context-content',
                '.readability-content',
                '.emotional-content',
                '.comparison-content'
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
    // Create error element if it doesn't exist
    let errorEl = document.getElementById('error-message');
    if (!errorEl) {
        errorEl = document.createElement('div');
        errorEl.id = 'error-message';
        errorEl.className = 'error-message';
        document.querySelector('.container').insertBefore(errorEl, document.querySelector('.input-section'));
    }
    
    errorEl.textContent = message;
    errorEl.style.display = 'block';
    
    // Hide after 5 seconds
    setTimeout(() => {
        errorEl.style.display = 'none';
    }, 5000);
}

// Toggle settings panel
function toggleSettings() {
    const settingsPanel = document.querySelector('.settings-panel');
    if (settingsPanel) {
        settingsPanel.classList.toggle('open');
    }
}

// Add all necessary styles
function addCardStyles() {
    const style = document.createElement('style');
    style.textContent = `
        /* Ensure consistent card heights and grid layout */
        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .analysis-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            transition: all 0.3s ease;
            min-height: 80px;
            display: flex;
            flex-direction: column;
        }
        
        .analysis-card.expanded {
            min-height: 300px;
        }
        
        .analysis-card:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .analysis-header {
            display: flex;
            align-items: center;
            padding: 15px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
            font-weight: 600;
            user-select: none;
            min-height: 60px;
        }
        
        .analysis-header:hover {
            background: #e9ecef;
        }
        
        .analysis-icon {
            font-size: 24px;
            margin-right: 12px;
        }
        
        /* Hide content by default for dropdown functionality */
        .card-content,
        .bias-content,
        .fact-check-content,
        .transparency-content,
        .author-content,
        .context-content,
        .readability-content,
        .emotional-content,
        .comparison-content {
            display: none;
            padding: 20px;
            animation: slideDown 0.3s ease;
            flex: 1;
            overflow-y: auto;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Progress bar styles */
        .progress-bar {
            display: none;
            width: 100%;
            max-width: 600px;
            height: 40px;
            background: #f0f0f0;
            border-radius: 20px;
            overflow: hidden;
            margin: 30px auto;
            position: relative;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #45a049);
            width: 0%;
            transition: width 0.4s ease;
            border-radius: 20px;
            position: relative;
            overflow: hidden;
        }
        
        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                45deg,
                rgba(255, 255, 255, 0.2) 25%,
                transparent 25%,
                transparent 50%,
                rgba(255, 255, 255, 0.2) 50%,
                rgba(255, 255, 255, 0.2) 75%,
                transparent 75%,
                transparent
            );
            background-size: 30px 30px;
            animation: progress-animation 1s linear infinite;
        }
        
        @keyframes progress-animation {
            0% {
                background-position: 0 0;
            }
            100% {
                background-position: 30px 0;
            }
        }
        
        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-weight: bold;
            font-size: 14px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
            z-index: 1;
        }
        
        /* Error message styles */
        .error-message {
            display: none;
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin: 20px auto;
            max-width: 600px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(204, 51, 51, 0.2);
        }
        
        /* Remove pro badges during development */
        .pro-indicator,
        .pro-badge,
        .upgrade-prompt,
        .lock-icon {
            display: none !important;
        }
        
        /* Dropdown arrow styles */
        .dropdown-arrow {
            font-size: 12px;
            color: #6b7280;
            margin-left: auto;
            transition: transform 0.3s ease;
        }
        
        /* Make all cards same height when expanded */
        .analysis-card.expanded {
            display: flex;
            flex-direction: column;
        }
        
        /* Ensure content sections fill available space */
        .analysis-card.expanded > div[style*="display: block"] {
            flex: 1;
            display: flex !important;
            flex-direction: column;
        }
    `;
    document.head.appendChild(style);
}

// Export for debugging
window.debugAnalysis = {
    getCurrentData: () => currentAnalysis,
    rerunDisplay: () => displayResults(currentAnalysis),
    testProgress: () => analyzeArticle('https://test.com')
};
