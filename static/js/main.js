// static/js/main.js - Complete Fixed Version
// Main application logic with correct API format

// Global state
let currentAnalysis = null;
let analysisInProgress = false;

// DOM elements
const urlInput = document.getElementById('urlInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsSection = document.getElementById('results');
const errorAlert = document.getElementById('errorAlert');
const errorMessage = document.getElementById('errorMessage');
const progressBar = document.querySelector('.progress-container');
const progressFill = document.querySelector('.progress-fill');
const progressText = document.querySelector('.progress-text');

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('News Analyzer initialized');
    
    // Set up event listeners
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', handleAnalyze);
    }
    
    if (urlInput) {
        urlInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !analysisInProgress) {
                handleAnalyze();
            }
        });
    }
    
    // Add example URL buttons
    setupExampleUrls();
    
    // Check for URL in query params
    checkUrlParams();
});

// Handle analyze button click
async function handleAnalyze() {
    const url = urlInput ? urlInput.value.trim() : '';
    
    if (!url) {
        showError('Please enter a valid URL');
        return;
    }
    
    if (!isValidUrl(url)) {
        showError('Please enter a valid news article URL');
        return;
    }
    
    await analyzeArticle(url);
}

// Main analysis function - FIXED API FORMAT
async function analyzeArticle(url) {
    if (analysisInProgress) {
        console.log('Analysis already in progress');
        return;
    }
    
    analysisInProgress = true;
    hideError();
    
    // Update UI
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = 'Analyzing...';
    }
    
    // Show progress bar
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
        // Make API call with CORRECT FORMAT
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })  // ← FIXED: Just { url } not { input: url, input_type: 'url' }
        });
        
        if (!response.ok) {
            const errorData = await response.text();
            throw new Error(errorData || `HTTP error! status: ${response.status}`);
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
    
    // Create cards for each analysis component
    const components = [
        { name: 'bias-analysis', data: data.bias_analysis, title: 'Bias Analysis' },
        { name: 'fact-checker', data: data.fact_checks || data.fact_checking, title: 'Fact Checking' },
        { name: 'transparency-analysis', data: data.transparency_analysis, title: 'Transparency' },
        { name: 'author-card', data: data.author_info || data.author_analysis, title: 'Author Analysis' },
        { name: 'context-card', data: data.context_analysis, title: 'Context' },
        { name: 'readability-card', data: data.readability_analysis || data.readability, title: 'Readability' },
        { name: 'emotional-tone-card', data: data.emotional_tone_analysis || data.emotional_tone, title: 'Emotional Tone' },
        { name: 'comparison-card', data: data.comparison_analysis || data.comparison, title: 'Source Comparison' }
    ];
    
    components.forEach(comp => {
        const card = createAnalysisCard(comp.name, comp.data, comp.title);
        if (card) {
            container.appendChild(card);
        }
    });
    
    // Update trust score if available
    updateTrustScore(data.trust_score);
    
    // Show article info
    if (data.article) {
        updateArticleInfo(data.article);
    }
}

// Create analysis card
function createAnalysisCard(componentName, data, title) {
    const card = document.createElement('div');
    card.className = 'analysis-card';
    card.setAttribute('data-component', componentName);
    
    // Basic card structure
    card.innerHTML = `
        <div class="card-header">
            <h3>${title}</h3>
            <button class="expand-btn" onclick="toggleCard('${componentName}')">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/>
                </svg>
            </button>
        </div>
        <div class="card-content" id="${componentName}-content">
            <div class="loading-placeholder">Loading component...</div>
        </div>
    `;
    
    // Load component dynamically
    loadComponent(componentName, data);
    
    return card;
}

// Load component dynamically
async function loadComponent(componentName, data) {
    try {
        // Check if component exists
        const ComponentClass = window[toCamelCase(componentName)];
        
        if (ComponentClass) {
            const instance = new ComponentClass();
            const content = await instance.render(data);
            
            const container = document.getElementById(`${componentName}-content`);
            if (container) {
                container.innerHTML = '';
                if (typeof content === 'string') {
                    container.innerHTML = content;
                } else {
                    container.appendChild(content);
                }
            }
        } else {
            console.warn(`Component ${componentName} not found`);
        }
    } catch (error) {
        console.error(`Error loading component ${componentName}:`, error);
    }
}

// Toggle card expansion
function toggleCard(componentName) {
    const card = document.querySelector(`[data-component="${componentName}"]`);
    if (card) {
        card.classList.toggle('expanded');
    }
}

// Update trust score display
function updateTrustScore(score) {
    const scoreElement = document.getElementById('trustScore');
    const scoreMeter = document.getElementById('trustScoreMeter');
    
    if (scoreElement && score !== undefined) {
        scoreElement.textContent = Math.round(score);
        
        // Update meter color based on score
        if (scoreMeter) {
            scoreMeter.style.width = `${score}%`;
            
            if (score >= 80) {
                scoreMeter.className = 'score-meter high';
            } else if (score >= 60) {
                scoreMeter.className = 'score-meter medium';
            } else {
                scoreMeter.className = 'score-meter low';
            }
        }
    }
}

// Update article info display
function updateArticleInfo(article) {
    const titleElement = document.getElementById('articleTitle');
    const sourceElement = document.getElementById('articleSource');
    const dateElement = document.getElementById('articleDate');
    
    if (titleElement && article.title) {
        titleElement.textContent = article.title;
    }
    
    if (sourceElement && article.domain) {
        sourceElement.textContent = article.domain;
    }
    
    if (dateElement && article.publish_date) {
        const date = new Date(article.publish_date);
        dateElement.textContent = date.toLocaleDateString();
    }
}

// Utility functions
function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

function showError(message) {
    if (errorAlert) {
        errorMessage.textContent = message;
        errorAlert.style.display = 'block';
    }
}

function hideError() {
    if (errorAlert) {
        errorAlert.style.display = 'none';
    }
}

function toCamelCase(str) {
    return str.split('-').map((word, index) => {
        if (index === 0) return word;
        return word.charAt(0).toUpperCase() + word.slice(1);
    }).join('');
}

// Setup example URLs
function setupExampleUrls() {
    const exampleUrls = [
        { text: 'CNN Politics', url: 'https://www.cnn.com/2024/01/25/politics/index.html' },
        { text: 'BBC Technology', url: 'https://www.bbc.com/news/technology' },
        { text: 'Reuters AI', url: 'https://www.reuters.com/technology/artificial-intelligence/' }
    ];
    
    const exampleContainer = document.getElementById('exampleUrls');
    if (exampleContainer) {
        exampleUrls.forEach(example => {
            const btn = document.createElement('button');
            btn.className = 'example-url-btn';
            btn.textContent = example.text;
            btn.onclick = () => {
                if (urlInput) {
                    urlInput.value = example.url;
                    handleAnalyze();
                }
            };
            exampleContainer.appendChild(btn);
        });
    }
}

// Check URL parameters
function checkUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const url = params.get('url');
    
    if (url && urlInput) {
        urlInput.value = url;
        // Auto-analyze if URL provided
        setTimeout(() => handleAnalyze(), 500);
    }
}

// Export functions for global use
window.analyzeArticle = analyzeArticle;
window.toggleCard = toggleCard;
window.currentAnalysis = () => currentAnalysis;
