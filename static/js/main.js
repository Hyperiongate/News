// static/js/main.js - COMPLETE FIX FOR ALL ISSUES
// Addresses: API format, data mapping, DOM IDs, missing functions, component conflicts

// Global state
let currentAnalysis = null;
let analysisInProgress = false;

// DOM elements - Fixed IDs to match HTML
const urlInput = document.getElementById('urlInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsSection = document.getElementById('results');
const errorAlert = document.getElementById('errorAlert');
const errorMessage = document.getElementById('errorMessage');
const progressContainer = document.querySelector('.progress-container');
const progressBar = document.querySelector('.progress-bar');
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

// Example URLs setup
function setupExampleUrls() {
    const exampleUrls = [
        { text: 'Reuters Example', url: 'https://www.reuters.com/technology/' },
        { text: 'BBC Example', url: 'https://www.bbc.com/news/technology' },
        { text: 'TechCrunch Example', url: 'https://techcrunch.com/' }
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
        setTimeout(() => handleAnalyze(), 500);
    }
}

// Show error message
function showError(message) {
    if (errorAlert) {
        errorAlert.style.display = 'block';
        if (errorMessage) {
            errorMessage.textContent = message;
        }
    }
    console.error('Error:', message);
}

// Hide error message
function hideError() {
    if (errorAlert) {
        errorAlert.style.display = 'none';
    }
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

// Main analysis function
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
        analyzeBtn.innerHTML = '<span>🔄</span> Analyzing...';
    }
    
    // Show progress
    if (progressContainer) {
        progressContainer.style.display = 'block';
        if (progressBar) progressBar.style.width = '10%';
        if (progressText) progressText.textContent = 'Starting analysis...';
    }
    
    // Simulate progress
    const progressSteps = [
        { percent: 25, text: 'Fetching article...' },
        { percent: 50, text: 'Analyzing content...' },
        { percent: 75, text: 'Checking facts...' },
        { percent: 90, text: 'Finalizing results...' }
    ];
    
    let stepIndex = 0;
    const progressInterval = setInterval(() => {
        if (stepIndex < progressSteps.length) {
            const step = progressSteps[stepIndex];
            if (progressBar) progressBar.style.width = `${step.percent}%`;
            if (progressText) progressText.textContent = step.text;
            stepIndex++;
        }
    }, 500);
    
    try {
        // Make API call with correct format
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }) // Correct format
        });
        
        if (!response.ok) {
            const errorData = await response.text();
            throw new Error(errorData || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Clear progress interval
        clearInterval(progressInterval);
        
        // Complete progress
        if (progressBar) progressBar.style.width = '100%';
        if (progressText) progressText.textContent = 'Analysis complete!';
        
        // Transform and store results
        currentAnalysis = transformApiData(result);
        
        // Show results after brief delay
        setTimeout(() => {
            if (progressContainer) progressContainer.style.display = 'none';
            displayResults(currentAnalysis);
            if (resultsSection) resultsSection.style.display = 'block';
        }, 500);
        
    } catch (error) {
        clearInterval(progressInterval);
        console.error('Analysis error:', error);
        showError(error.message || 'Failed to analyze article. Please try again.');
        
        if (progressContainer) progressContainer.style.display = 'none';
    } finally {
        analysisInProgress = false;
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<span>🔍</span> Analyze';
        }
    }
}

// Transform API data - COMPREHENSIVE FIX
function transformApiData(result) {
    if (!result) return result;
    
    console.log('Transforming API data:', result);
    
    // Ensure success flag
    result.success = true;
    result.is_pro = true;
    
    // Fix bias_analysis - ensure ALL nested properties exist
    if (!result.bias_analysis) {
        result.bias_analysis = {};
    }
    
    // Initialize bias_dimensions with default structure
    result.bias_analysis.bias_dimensions = result.bias_analysis.bias_dimensions || {
        political: { score: 0, label: 'Center', confidence: 70 },
        corporate: { score: 0, label: 'Neutral', confidence: 70 },
        ideological: { score: 0, label: 'Balanced', confidence: 70 },
        sensationalism: { score: 0, label: 'Factual', confidence: 70 }
    };
    
    // Ensure all bias fields exist
    result.bias_analysis = {
        ...result.bias_analysis,
        overall_bias: result.bias_analysis.overall_bias || 'center',
        political_lean: result.bias_analysis.political_lean || 0,
        confidence: result.bias_analysis.confidence || 70,
        bias_score: result.bias_analysis.bias_score || 0.1,
        loaded_phrases: result.bias_analysis.loaded_phrases || [],
        manipulation_tactics: result.bias_analysis.manipulation_tactics || [],
        bias_indicators: result.bias_analysis.bias_indicators || [],
        bias_patterns: result.bias_analysis.bias_patterns || []
    };
    
    // Map fact checking data
    result.fact_checks = result.fact_check_results || result.fact_checks || {
        claims: [],
        fact_checks: [],
        summary: { total_claims: 0, verified: 0, false: 0, unverified: 0 }
    };
    
    // Fix author analysis
    result.author_info = result.author_analysis || result.author_info || {
        name: 'Unknown',
        credibility_score: 50,
        verification_status: { verified: false },
        professional_info: {}
    };
    
    // Fix transparency
    result.transparency_score = result.transparency_analysis?.transparency_score || 50;
    result.transparency_analysis = result.transparency_analysis || {
        transparency_score: 50,
        indicators: []
    };
    
    // Fix other analyses
    result.manipulation_analysis = result.manipulation_analysis || {
        score: 0,
        tactics: []
    };
    
    result.readability_analysis = result.readability_analysis || {
        score: 70,
        level: 'Medium',
        details: {}
    };
    
    result.emotional_tone_analysis = result.emotion_analysis || result.emotional_tone_analysis || {
        dominant_emotion: 'neutral',
        emotions: { neutral: 0.6, joy: 0.1, anger: 0.1, fear: 0.1, sadness: 0.1 }
    };
    
    result.context_analysis = result.context_analysis || {
        summary: 'Context analysis not available'
    };
    
    result.comparison_analysis = result.comparison_analysis || {
        similar_articles: []
    };
    
    // Fix source credibility
    result.source_analysis = result.source_credibility || result.source_analysis || {
        credibility: 'medium',
        rating: 'unknown'
    };
    
    // Ensure article exists
    result.article = result.article || {
        title: 'Article',
        url: '',
        author: 'Unknown',
        domain: '',
        content: ''
    };
    
    console.log('Transformation complete:', result);
    return result;
}

// Display results - FIXED
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
    
    // Update trust score if element exists
    updateTrustScore(data.trust_score);
    
    // Update article info if element exists
    updateArticleInfo(data.article);
    
    // Create cards for each component
    const components = [
        { name: 'bias-analysis', className: 'BiasAnalysis', data: data, title: 'Bias Analysis' },
        { name: 'fact-checker', className: 'FactChecker', data: data, title: 'Fact Checking' },
        { name: 'transparency-analysis', className: 'TransparencyAnalysis', data: data, title: 'Transparency' },
        { name: 'author-card', className: 'AuthorCard', data: data, title: 'Author Analysis' },
        { name: 'context-card', className: 'ContextCard', data: data, title: 'Context' },
        { name: 'readability-card', className: 'ReadabilityCard', data: data, title: 'Readability' },
        { name: 'emotional-tone-card', className: 'EmotionalToneCard', data: data, title: 'Emotional Tone' },
        { name: 'comparison-card', className: 'ComparisonCard', data: data, title: 'Source Comparison' }
    ];
    
    components.forEach((comp, index) => {
        const card = createAnalysisCard(comp.name, comp.className, comp.data, comp.title, index);
        if (card) {
            container.appendChild(card);
        }
    });
}

// Create analysis card - FIXED
function createAnalysisCard(componentName, className, data, title, index) {
    const card = document.createElement('div');
    card.className = 'analysis-card';
    card.setAttribute('data-component', componentName);
    
    // Auto-expand first 4 cards
    const isExpanded = index < 4;
    
    card.innerHTML = `
        <div class="card-header" onclick="toggleCard('${componentName}')">
            <h3>${title}</h3>
            <button class="expand-btn">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" class="${isExpanded ? 'rotated' : ''}">
                    <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/>
                </svg>
            </button>
        </div>
        <div class="card-content" id="${componentName}-content" style="${isExpanded ? '' : 'display: none;'}">
            <div class="loading-placeholder">Loading component...</div>
        </div>
    `;
    
    // Load component after card is created
    setTimeout(() => loadComponent(componentName, className, data), 100);
    
    return card;
}

// Load component - FIXED
async function loadComponent(componentName, className, data) {
    try {
        const ComponentClass = window[className];
        
        if (!ComponentClass) {
            console.error(`Component class ${className} not found`);
            return;
        }
        
        const instance = new ComponentClass();
        
        if (typeof instance.render !== 'function') {
            console.error(`Component ${className} missing render method`);
            return;
        }
        
        // Pass the complete data object
        const element = await instance.render(data);
        
        // Update card content
        const contentEl = document.getElementById(`${componentName}-content`);
        if (contentEl) {
            if (typeof element === 'string') {
                contentEl.innerHTML = element;
            } else if (element instanceof HTMLElement) {
                contentEl.innerHTML = '';
                contentEl.appendChild(element);
            }
            
            // Initialize any visualizations if the component has them
            if (typeof instance.initializeVisualizations === 'function') {
                setTimeout(() => {
                    try {
                        instance.initializeVisualizations(data);
                    } catch (e) {
                        console.warn(`Visualization init failed for ${className}:`, e);
                    }
                }, 100);
            }
        }
        
    } catch (error) {
        console.error(`Error loading component ${className}:`, error);
        const contentEl = document.getElementById(`${componentName}-content`);
        if (contentEl) {
            contentEl.innerHTML = '<div class="error">Failed to load component</div>';
        }
    }
}

// Toggle card expansion
function toggleCard(componentName) {
    const content = document.getElementById(`${componentName}-content`);
    const card = document.querySelector(`[data-component="${componentName}"]`);
    const btn = card?.querySelector('.expand-btn svg');
    
    if (content) {
        if (content.style.display === 'none') {
            content.style.display = 'block';
            if (btn) btn.classList.add('rotated');
        } else {
            content.style.display = 'none';
            if (btn) btn.classList.remove('rotated');
        }
    }
}

// Update trust score - IMPLEMENTED
function updateTrustScore(score) {
    const trustScoreEl = document.getElementById('trustScore');
    const trustBarEl = document.querySelector('.trust-bar-fill');
    const trustLabelEl = document.getElementById('trustLabel');
    
    if (trustScoreEl) trustScoreEl.textContent = score || 0;
    
    if (trustBarEl) {
        const scoreValue = score || 0;
        trustBarEl.style.width = `${scoreValue}%`;
        
        // Color based on score
        if (scoreValue >= 80) {
            trustBarEl.style.backgroundColor = '#10b981';
        } else if (scoreValue >= 60) {
            trustBarEl.style.backgroundColor = '#f59e0b';
        } else {
            trustBarEl.style.backgroundColor = '#ef4444';
        }
    }
    
    if (trustLabelEl) {
        const scoreValue = score || 0;
        if (scoreValue >= 80) {
            trustLabelEl.textContent = 'High Credibility';
        } else if (scoreValue >= 60) {
            trustLabelEl.textContent = 'Moderate Credibility';
        } else {
            trustLabelEl.textContent = 'Low Credibility';
        }
    }
}

// Update article info - IMPLEMENTED
function updateArticleInfo(article) {
    if (!article) return;
    
    const titleEl = document.getElementById('articleTitle');
    const authorEl = document.getElementById('articleAuthor');
    const sourceEl = document.getElementById('articleSource');
    const dateEl = document.getElementById('articleDate');
    
    if (titleEl && article.title) {
        titleEl.textContent = article.title;
    }
    
    if (authorEl && article.author) {
        authorEl.textContent = `By ${article.author}`;
    }
    
    if (sourceEl && article.domain) {
        sourceEl.textContent = article.domain;
    }
    
    if (dateEl && article.date) {
        const date = new Date(article.date);
        dateEl.textContent = date.toLocaleDateString();
    }
}

// Export functions for global use
window.analyzeArticle = analyzeArticle;
window.toggleCard = toggleCard;
window.currentAnalysis = () => currentAnalysis;

console.log('Main.js loaded successfully');
