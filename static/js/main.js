// static/js/main.js - COMPLETE FIXED VERSION
// Single unified system for component loading and rendering

// Global state
let currentAnalysis = null;
let analysisInProgress = false;

// DOM elements
const urlInput = document.getElementById('url-input');
const analyzeBtn = document.getElementById('analyze-btn');
const resultsSection = document.getElementById('results-section');
const errorAlert = document.getElementById('errorAlert');
const errorMessage = document.getElementById('errorMessage');
const progressBar = document.querySelector('.progress-container');
const progressFill = document.querySelector('.progress-fill');
const progressText = document.querySelector('.progress-text');

// Component mapping
const COMPONENT_MAP = {
    'bias-analysis': 'BiasAnalysis',
    'fact-checker': 'FactChecker',
    'transparency-analysis': 'TransparencyAnalysis',
    'author-card': 'AuthorCard',
    'context-card': 'ContextCard',
    'readability-card': 'ReadabilityCard',
    'emotional-tone-card': 'EmotionalToneCard',
    'comparison-card': 'ComparisonCard'
};

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
    
    // Check for URL in query params
    const params = new URLSearchParams(window.location.search);
    const url = params.get('url');
    if (url && urlInput) {
        urlInput.value = url;
        setTimeout(() => handleAnalyze(), 500);
    }
    
    // Verify components loaded
    verifyComponents();
});

// Verify all components are loaded
function verifyComponents() {
    console.log('Verifying components...');
    Object.entries(COMPONENT_MAP).forEach(([key, className]) => {
        if (window[className]) {
            console.log(`✅ ${className} loaded`);
        } else {
            console.error(`❌ ${className} NOT loaded`);
        }
    });
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
async function analyzeArticle(inputUrl) {
    if (analysisInProgress) return;
    
    analysisInProgress = true;
    hideError();
    
    // Update UI
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span>🔄</span> Analyzing...';
    }
    
    // Show progress
    showProgress();
    
    try {
        // API call with CORRECT format
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: inputUrl }) // Just { url }, not { input: url, input_type: 'url' }
        });
        
        if (!response.ok) {
            const errorData = await response.text();
            throw new Error(errorData || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Check if the server returned an error
        if (result.error) {
            throw new Error(result.error);
        }
        
        // Store and transform results
        currentAnalysis = transformApiData(result, inputUrl);
        
        // FIXED: Set window.currentAnalysis as the data, not a function
        window.currentAnalysis = currentAnalysis;
        
        // Complete progress
        updateProgress(100, 'Analysis complete!');
        
        // Show results after brief delay
        setTimeout(() => {
            hideProgress();
            displayResults(currentAnalysis);
        }, 500);
        
    } catch (error) {
        console.error('Analysis error:', error);
        let errorMsg = 'Failed to analyze article. ';
        
        // Provide more specific error messages
        if (error.message.includes('timeout') || error.message.includes('timed out')) {
            errorMsg += 'The website took too long to respond. Try a different article.';
        } else if (error.message.includes('HTTPSConnectionPool')) {
            errorMsg += 'Could not connect to the website. It may be blocking automated access.';
        } else {
            errorMsg += error.message || 'Please try again.';
        }
        
        showError(errorMsg);
        hideProgress();
    } finally {
        analysisInProgress = false;
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<span>🔍</span> Analyze';
        }
    }
}

// Transform API data to match component expectations
function transformApiData(result, originalUrl) {
    if (!result) return null;
    
    console.log('Transforming API data...');
    
    // Ensure all expected fields exist
    const transformed = {
        ...result,
        success: true,
        is_pro: true,
        
        // Map fields for components
        bias_analysis: result.bias_analysis || {},
        fact_checks: result.fact_checks || result.fact_checking || [],
        transparency_analysis: result.transparency_analysis || {},
        author_analysis: result.author_analysis || result.author_info || {},
        context_analysis: result.context_analysis || result.network_analysis || {},
        readability_analysis: result.readability_analysis || result.readability || {},
        emotional_tone_analysis: result.emotional_tone_analysis || result.emotion_analysis || {},
        comparison_analysis: result.comparison_analysis || {
            source_credibility: result.source_credibility || {},
            similar_coverage: result.network_analysis?.related_articles || 0,
            consensus_score: result.trust_score || 50
        },
        
        // Ensure article data exists - FIXED: use originalUrl parameter
        article: {
            ...result.article,
            url: result.article?.url || originalUrl,
            title: result.article?.title || 'Untitled',
            author: result.article?.author || 'Unknown',
            domain: result.article?.domain || (result.article?.url ? new URL(result.article.url).hostname : (originalUrl ? new URL(originalUrl).hostname : 'unknown'))
        },
        
        // Scores
        trust_score: result.trust_score || 0,
        bias_score: result.bias_analysis?.political_lean || 0
    };
    
    return transformed;
}

// Display results
function displayResults(data) {
    if (!data || !data.success) {
        showError('No results to display');
        return;
    }
    
    // Show results section
    if (resultsSection) {
        resultsSection.style.display = 'block';
    }
    
    // Update trust score
    updateTrustScore(data.trust_score);
    
    // Show trust score section
    const trustSection = document.getElementById('trust-score-section');
    if (trustSection) {
        trustSection.classList.remove('hidden');
    }
    
    // Get or create results grid
    let container = document.querySelector('.results-grid');
    if (!container) {
        container = document.createElement('div');
        container.className = 'results-grid';
        resultsSection.appendChild(container);
    }
    
    // Clear previous results
    container.innerHTML = '';
    
    // Create cards for each component
    const cards = [
        { id: 'bias-analysis', title: 'Bias Analysis', icon: '⚖️' },
        { id: 'fact-checker', title: 'Fact Checking', icon: '✓' },
        { id: 'transparency-analysis', title: 'Transparency', icon: '🔍' },
        { id: 'author-card', title: 'Author Analysis', icon: '👤' },
        { id: 'context-card', title: 'Context', icon: '🌐' },
        { id: 'readability-card', title: 'Readability', icon: '📖' },
        { id: 'emotional-tone-card', title: 'Emotional Tone', icon: '😊' },
        { id: 'comparison-card', title: 'Source Comparison', icon: '📊' }
    ];
    
    cards.forEach((cardInfo, index) => {
        const card = createAnalysisCard(cardInfo, data);
        container.appendChild(card);
        
        // Auto-expand first 4 cards
        if (index < 4) {
            setTimeout(() => {
                card.classList.add('expanded');
            }, 100 + (index * 50));
        }
    });
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Create analysis card
function createAnalysisCard(cardInfo, data) {
    const card = document.createElement('div');
    card.className = 'analysis-card';
    card.setAttribute('data-component', cardInfo.id);
    
    // Create card structure
    card.innerHTML = `
        <div class="card-header">
            <h3>${cardInfo.icon} ${cardInfo.title}</h3>
            <button class="expand-btn" onclick="toggleCard('${cardInfo.id}')">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/>
                </svg>
            </button>
        </div>
        <div class="card-content">
            <div class="loading-placeholder">Loading component...</div>
        </div>
    `;
    
    // Load component content after card is in DOM
    setTimeout(() => {
        loadComponent(cardInfo.id, data, card.querySelector('.card-content'));
    }, 50);
    
    return card;
}

// Load component into card
function loadComponent(componentId, data, container) {
    try {
        const className = COMPONENT_MAP[componentId];
        const ComponentClass = window[className];
        
        if (!ComponentClass) {
            console.error(`Component ${className} not found`);
            container.innerHTML = '<p style="color: #666; padding: 20px;">Component not available</p>';
            return;
        }
        
        // Create component instance
        const component = new ComponentClass();
        
        // Render component with full data
        const rendered = component.render(data);
        
        // Clear loading message
        container.innerHTML = '';
        
        // Insert rendered content
        if (rendered instanceof HTMLElement) {
            container.appendChild(rendered);
        } else if (typeof rendered === 'string') {
            container.innerHTML = rendered;
        } else {
            console.error(`Unexpected render result from ${className}`);
            container.innerHTML = '<p style="color: #666;">Error rendering component</p>';
        }
        
        // Initialize any visualizations
        if (typeof component.initializeVisualizations === 'function') {
            setTimeout(() => component.initializeVisualizations(), 100);
        }
        
    } catch (error) {
        console.error(`Error loading ${componentId}:`, error);
        container.innerHTML = '<p style="color: #dc2626;">Error loading component</p>';
    }
}

// Toggle card expansion
window.toggleCard = function(componentId) {
    const card = document.querySelector(`[data-component="${componentId}"]`);
    if (card) {
        card.classList.toggle('expanded');
    }
};

// Progress bar functions
function showProgress() {
    if (progressBar) {
        progressBar.style.display = 'block';
        updateProgress(0, 'Starting analysis...');
        
        // Simulate progress
        const steps = [
            { percent: 10, text: 'Fetching article...', delay: 400 },
            { percent: 25, text: 'Analyzing bias...', delay: 800 },
            { percent: 40, text: 'Fact-checking claims...', delay: 1200 },
            { percent: 55, text: 'Evaluating transparency...', delay: 1600 },
            { percent: 70, text: 'Researching author...', delay: 2000 },
            { percent: 85, text: 'Analyzing context...', delay: 2400 }
        ];
        
        steps.forEach(step => {
            setTimeout(() => {
                if (analysisInProgress) {
                    updateProgress(step.percent, step.text);
                }
            }, step.delay);
        });
    }
}

function updateProgress(percent, text) {
    if (progressFill) progressFill.style.width = `${percent}%`;
    if (progressText) progressText.textContent = text;
}

function hideProgress() {
    if (progressBar) progressBar.style.display = 'none';
}

// Update trust score display
function updateTrustScore(score) {
    const scoreElement = document.getElementById('trustScore');
    const scoreMeter = document.querySelector('.score-meter');
    
    if (scoreElement) {
        scoreElement.textContent = Math.round(score);
    }
    
    if (scoreMeter) {
        scoreMeter.style.width = `${score}%`;
        scoreMeter.className = 'score-meter';
        
        if (score >= 80) {
            scoreMeter.classList.add('high');
        } else if (score >= 60) {
            scoreMeter.classList.add('medium');
        } else {
            scoreMeter.classList.add('low');
        }
    }
}

// Error handling
function showError(message) {
    if (errorAlert && errorMessage) {
        errorMessage.textContent = message;
        errorAlert.style.display = 'block';
    }
}

function hideError() {
    if (errorAlert) {
        errorAlert.style.display = 'none';
    }
}

// Utility function
function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

// Example URLs setup
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

// Call setupExampleUrls on load if container exists
document.addEventListener('DOMContentLoaded', function() {
    setupExampleUrls();
});

// Export for testing
window.analyzeArticle = analyzeArticle;
window.currentAnalysis = currentAnalysis;

// Auto-run tests in development
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    window.addEventListener('load', function() {
        console.log('Development mode - Running component tests...');
        
        // Test each component
        const testData = {
            success: true,
            is_pro: true,
            bias_analysis: { political_lean: 0.3, confidence: 85 },
            fact_checks: [{ claim: 'Test claim', verdict: 'verified' }],
            transparency_analysis: { score: 75 },
            author_analysis: { name: 'Test Author', credibility_score: 80 },
            context_analysis: { related_articles: 5 },
            readability_analysis: { score: 65 },
            emotional_tone_analysis: { dominant: 'neutral' },
            comparison_analysis: { consensus_score: 70 },
            article: { title: 'Test Article', url: 'https://example.com' },
            trust_score: 75
        };
        
        Object.entries(COMPONENT_MAP).forEach(([id, className]) => {
            try {
                const ComponentClass = window[className];
                if (ComponentClass) {
                    const instance = new ComponentClass();
                    const result = instance.render(testData);
                    if (result) {
                        console.log(`✅ ${className} test passed`);
                    } else {
                        console.error(`❌ ${className} test failed - no render output`);
                    }
                }
            } catch (e) {
                console.error(`❌ ${className} test failed:`, e);
            }
        });
    });
}
