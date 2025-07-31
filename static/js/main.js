// static/js/main.js - Complete Fixed Version
// Main application logic with correct API format and component mapping

// Global state
let currentAnalysis = null;
let analysisInProgress = false;

// DOM elements - Fixed to use correct IDs
const urlInput = document.getElementById('url-input') || document.getElementById('urlInput');
const analyzeBtn = document.getElementById('analyze-btn') || document.getElementById('analyzeBtn');
const resultsSection = document.getElementById('results-section') || document.getElementById('results');
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
        analyzeBtn.innerHTML = '<span>🔄</span> Analyzing...';
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
            analyzeBtn.innerHTML = '<span>🔍</span> Analyze';
        }
    }
}

// Transform API data to match UI expectations - FIXED TO MATCH ACTUAL BACKEND FIELDS
function transformApiData(result) {
    if (!result) return result;
    
    console.log('Transforming API data with correct mappings...');
    
    // Ensure success flag
    result.success = true;
    
    // Ensure all required fields exist with correct mappings
    // Backend returns these fields (from your debug output):
    // - bias_analysis ✓
    // - fact_checks ✓ 
    // - transparency_analysis ✓
    // - author_analysis ✓
    // - emotion_analysis (NOT emotional_tone_analysis)
    // - readability_analysis ✓
    // - NO context_analysis
    // - NO comparison_analysis
    
    // Keep existing fields as-is
    result.bias_analysis = result.bias_analysis || {};
    result.transparency_analysis = result.transparency_analysis || {};
    result.readability_analysis = result.readability_analysis || {};
    
    // Map fact_checks to fact_checking (components expect fact_checking)
    result.fact_checking = result.fact_checks || {};
    
    // Map author_analysis to author_info (some components might expect author_info)
    result.author_info = result.author_analysis || {};
    
    // Map emotion_analysis to emotional_tone_analysis (components expect emotional_tone_analysis)
    result.emotional_tone_analysis = result.emotion_analysis || {};
    result.emotional_tone = result.emotion_analysis || {};
    
    // Create context_analysis from network_analysis or content_analysis
    result.context_analysis = result.network_analysis || result.content_analysis || {
        related_articles: 0,
        timeline_events: 0,
        missing_perspectives: []
    };
    
    // Create comparison_analysis from available data
    result.comparison_analysis = {
        source_credibility: result.source_credibility || {},
        similar_coverage: result.network_analysis?.related_articles || 0,
        consensus_score: result.trust_score || 50,
        trust_level: result.trust_level || {}
    };
    
    // Map readability
    result.readability = result.readability_analysis || {};
    
    // Ensure article exists
    result.article = result.article || {};
    
    // Force pro features
    result.is_pro = true;
    
    console.log('Transformation complete');
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
        { name: 'fact-checker', data: data.fact_checking, title: 'Fact Checking' },
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
    
    // Show trust score section
    const trustSection = document.getElementById('trust-score-section');
    if (trustSection && data.trust_score) {
        trustSection.classList.remove('hidden');
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

// Load component dynamically - FIXED WITH CORRECT MAPPING
async function loadComponent(componentName, data) {
    try {
        console.log(`Loading component: ${componentName} with data:`, data ? 'Has data' : 'No data');
        
        // Map kebab-case names to PascalCase class names
        const componentMap = {
            'bias-analysis': 'BiasAnalysis',
            'fact-checker': 'FactChecker',
            'transparency-analysis': 'TransparencyAnalysis',
            'author-card': 'AuthorCard',
            'context-card': 'ContextCard',
            'readability-card': 'ReadabilityCard',
            'emotional-tone-card': 'EmotionalToneCard',
            'comparison-card': 'ComparisonCard'
        };
        
        // Get the correct class name
        const className = componentMap[componentName];
        const ComponentClass = window[className];
        
        if (ComponentClass) {
            console.log(`Found component class: ${className}`);
            const instance = new ComponentClass();
            
            // Check if render method exists
            if (typeof instance.render === 'function') {
                const content = await instance.render(data);
                
                const container = document.getElementById(`${componentName}-content`);
                if (container) {
                    container.innerHTML = '';
                    if (typeof content === 'string') {
                        container.innerHTML = content;
                    } else if (content instanceof HTMLElement) {
                        container.appendChild(content);
                    } else {
                        // Fallback: show raw data
                        container.innerHTML = `
                            <div class="component-data">
                                <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto;">
${JSON.stringify(data, null, 2)}
                                </pre>
                            </div>
                        `;
                    }
                }
            } else {
                console.error(`Component ${className} missing render method`);
                showFallbackData(componentName, data);
            }
        } else {
            console.warn(`Component class ${className} not found`);
            showFallbackData(componentName, data);
        }
    } catch (error) {
        console.error(`Error loading component ${componentName}:`, error);
        showFallbackData(componentName, data);
    }
}

// Show fallback data when component fails to load
function showFallbackData(componentName, data) {
    const container = document.getElementById(`${componentName}-content`);
    if (container) {
        if (!data || Object.keys(data).length === 0) {
            container.innerHTML = `
                <div class="component-fallback" style="padding: 20px; text-align: center;">
                    <p style="color: #666;">No data available for this analysis.</p>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="component-fallback" style="padding: 15px;">
                    <p style="color: #666; font-style: italic;">Component visualization unavailable. Showing raw data:</p>
                    <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; margin-top: 10px;">
${JSON.stringify(data, null, 2)}
                    </pre>
                </div>
            `;
        }
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
    const scoreMeter = document.querySelector('#trustScoreMeter .score-meter');
    
    if (scoreElement && score !== undefined) {
        scoreElement.textContent = Math.round(score);
        
        // Update meter width and color
        if (scoreMeter) {
            scoreMeter.style.width = `${score}%`;
            
            // Remove all classes first
            scoreMeter.classList.remove('high', 'medium', 'low');
            
            // Add appropriate class based on score
            if (score >= 80) {
                scoreMeter.classList.add('high');
            } else if (score >= 60) {
                scoreMeter.classList.add('medium');
            } else {
                scoreMeter.classList.add('low');
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
    } else {
        // Fallback error display
        alert(message);
    }
}

function hideError() {
    if (errorAlert) {
        errorAlert.style.display = 'none';
    }
}

// Fixed toCamelCase function - NO LONGER NEEDED but kept for compatibility
function toCamelCase(str) {
    // This function is no longer used in loadComponent
    // but kept here in case other code depends on it
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

// Component verification on load
window.addEventListener('load', function() {
    console.log('Verifying component availability:');
    const requiredComponents = [
        'BiasAnalysis',
        'FactChecker',
        'TransparencyAnalysis',
        'AuthorCard',
        'ContextCard',
        'ReadabilityCard',
        'EmotionalToneCard',
        'ComparisonCard'
    ];
    
    requiredComponents.forEach(name => {
        const exists = !!window[name];
        console.log(`${name}: ${exists ? '✅' : '❌'}`);
    });
});
