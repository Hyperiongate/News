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

// Transform API data to match UI expectations - COMPREHENSIVE MAPPING
function transformApiData(result) {
    if (!result) return result;
    
    console.log('Transforming API data:', result);
    
    // Ensure success flag
    result.success = true;
    
    // Force pro features
    result.is_pro = true;
    
    // Map all the fields that components expect
    
    // 1. Map bias fields for BiasAnalysis component
    if (result.bias_analysis) {
        // The BiasAnalysis component looks for these at the root level
        result.bias_score = result.bias_analysis.political_lean || result.bias_analysis.bias_score || 0;
        result.bias_confidence = result.bias_analysis.confidence || result.bias_analysis.bias_confidence || 70;
        
        // Ensure bias_analysis has all expected fields
        result.bias_analysis = {
            ...result.bias_analysis,
            overall_bias: result.bias_analysis.overall_bias || (
                result.bias_analysis.political_lean > 0.3 ? 'right' :
                result.bias_analysis.political_lean < -0.3 ? 'left' : 'center'
            ),
            political_lean: result.bias_analysis.political_lean || 0,
            confidence: result.bias_analysis.confidence || 70,
            bias_dimensions: result.bias_analysis.bias_dimensions || {},
            loaded_phrases: result.bias_analysis.loaded_phrases || [],
            manipulation_tactics: result.bias_analysis.manipulation_tactics || [],
            bias_indicators: result.bias_analysis.bias_indicators || []
        };
    }
    
    // 2. Map clickbait fields
    if (result.clickbait_analysis) {
        result.clickbait_score = result.clickbait_analysis.score || 0;
        
        // Ensure clickbait_analysis has expected structure
        result.clickbait_analysis = {
            ...result.clickbait_analysis,
            score: result.clickbait_analysis.score || 0,
            tactics: result.clickbait_analysis.tactics || [],
            elements: result.clickbait_analysis.elements || []
        };
    }
    
    // 3. Map fact checking fields
    if (result.fact_checks) {
        // Ensure it's in the expected format
        result.fact_checks = Array.isArray(result.fact_checks) ? 
            result.fact_checks : (result.fact_checks.claims || []);
    }
    
    // 4. Map author fields
    if (result.author_analysis) {
        result.author_info = result.author_analysis;
        
        // Ensure author has expected fields
        result.author_analysis = {
            ...result.author_analysis,
            found: result.author_analysis.found !== undefined ? result.author_analysis.found : false,
            credibility_score: result.author_analysis.credibility_score || 50,
            name: result.author_analysis.name || result.article?.author || 'Unknown',
            position: result.author_analysis.position || null,
            organization: result.author_analysis.organization || null,
            expertise: result.author_analysis.expertise || [],
            social_media: result.author_analysis.social_media || {},
            verification_status: result.author_analysis.verification_status || {}
        };
    }
    
    // 5. Map transparency fields
    if (result.transparency_analysis) {
        result.transparency_score = result.transparency_analysis.score || 0;
        
        result.transparency_analysis = {
            ...result.transparency_analysis,
            score: result.transparency_analysis.score || 0,
            factors: result.transparency_analysis.factors || [],
            missing_elements: result.transparency_analysis.missing_elements || []
        };
    }
    
    // 6. Map emotion/emotional tone fields
    if (result.emotion_analysis) {
        result.emotional_tone_analysis = result.emotion_analysis;
        result.emotional_tone = result.emotion_analysis;
    }
    
    // 7. Map readability fields
    if (result.readability_analysis) {
        result.readability = result.readability_analysis;
    }
    
    // 8. Create missing analysis sections that components expect
    result.context_analysis = result.network_analysis || result.content_analysis || {
        related_articles: 0,
        timeline_events: 0,
        missing_perspectives: [],
        sources_cited: 0
    };
    
    result.comparison_analysis = {
        source_credibility: result.source_credibility || {},
        similar_coverage: result.network_analysis?.related_articles || 0,
        consensus_score: result.trust_score || 50,
        trust_level: result.trust_level || {}
    };
    
    // 9. Map manipulation analysis
    if (result.manipulation_analysis) {
        result.manipulation_analysis = {
            ...result.manipulation_analysis,
            score: result.manipulation_analysis.score || 0,
            tactics: result.manipulation_analysis.tactics || [],
            techniques: result.manipulation_analysis.techniques || []
        };
    }
    
    // 10. Map source credibility
    if (result.source_credibility) {
        result.source_credibility = {
            ...result.source_credibility,
            credibility: result.source_credibility.credibility || 'Unknown',
            bias: result.source_credibility.bias || 'Unknown',
            factual_reporting: result.source_credibility.factual_reporting || 'Unknown'
        };
    }
    
    // 11. Ensure article exists with all fields
    result.article = result.article || {};
    result.article = {
        ...result.article,
        url: result.article.url || url,
        title: result.article.title || '',
        author: result.article.author || 'Unknown',
        content: result.article.content || result.article.text || '',
        domain: result.article.domain || (result.article.url ? new URL(result.article.url).hostname : ''),
        publish_date: result.article.publish_date || result.article.date || null
    };
    
    // 12. Map article metrics
    result.article_metrics = result.content_analysis || {
        readability: result.readability_analysis || {},
        word_count: result.article.word_count || 0,
        sentence_count: result.article.sentence_count || 0,
        paragraph_count: result.article.paragraph_count || 0,
        engagement: {
            estimated_read_time: result.article.reading_time || '0 min'
        }
    };
    
    console.log('Transformation complete:', result);
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
        { name: 'bias-analysis', data: data, title: 'Bias Analysis' },
        { name: 'fact-checker', data: data, title: 'Fact Checking' },
        { name: 'transparency-analysis', data: data, title: 'Transparency' },
        { name: 'author-card', data: data, title: 'Author Analysis' },
        { name: 'context-card', data: data, title: 'Context' },
        { name: 'readability-card', data: data, title: 'Readability' },
        { name: 'emotional-tone-card', data: data, title: 'Emotional Tone' },
        { name: 'comparison-card', data: data, title: 'Source Comparison' }
    ];
    
    components.forEach((comp, index) => {
        const card = createAnalysisCard(comp.name, comp.data, comp.title);
        if (card) {
            container.appendChild(card);
            // Auto-expand first 4 cards
            if (index < 4) {
                setTimeout(() => {
                    card.classList.add('expanded');
                }, 100 + (index * 50));
            }
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

// Create analysis card - COMPLETELY REWRITTEN
function createAnalysisCard(componentName, data, title) {
    const card = document.createElement('div');
    card.className = 'analysis-card';
    card.setAttribute('data-component', componentName);
    
    // Create card header
    const header = document.createElement('div');
    header.className = 'card-header';
    header.innerHTML = `
        <h3>${title}</h3>
        <button class="expand-btn">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/>
            </svg>
        </button>
    `;
    
    // Create card content container
    const content = document.createElement('div');
    content.className = 'card-content';
    content.id = `${componentName}-content`;
    
    // Add click handler to header
    header.addEventListener('click', () => {
        card.classList.toggle('expanded');
    });
    
    // Assemble card
    card.appendChild(header);
    card.appendChild(content);
    
    // Load component content asynchronously
    setTimeout(() => {
        loadComponentContent(componentName, data, content);
    }, 50);
    
    return card;
}

// Load component content - COMPLETELY NEW APPROACH
function loadComponentContent(componentName, data, container) {
    try {
        console.log(`Loading ${componentName} content...`);
        
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
        
        const className = componentMap[componentName];
        const ComponentClass = window[className];
        
        if (!ComponentClass) {
            console.error(`Component class ${className} not found`);
            container.innerHTML = '<p style="color: #666; padding: 20px;">Component not available</p>';
            return;
        }
        
        // Create component instance
        const component = new ComponentClass();
        
        // Render component
        if (typeof component.render === 'function') {
            const rendered = component.render(data);
            
            // Clear container
            container.innerHTML = '';
            
            // Handle different return types
            if (rendered instanceof HTMLElement) {
                // It's an HTML element - append it
                container.appendChild(rendered);
            } else if (typeof rendered === 'string') {
                // It's an HTML string - set innerHTML
                container.innerHTML = rendered;
            } else if (rendered && typeof rendered.outerHTML === 'string') {
                // It has outerHTML - use that
                container.innerHTML = rendered.outerHTML;
            } else {
                console.error(`Unexpected render result from ${className}:`, rendered);
                container.innerHTML = '<p style="color: #666; padding: 20px;">Error rendering component</p>';
            }
            
            // Call post-render initialization if it exists
            if (typeof component.initializeVisualizations === 'function') {
                setTimeout(() => {
                    try {
                        component.initializeVisualizations();
                    } catch (e) {
                        console.error(`Error initializing visualizations for ${className}:`, e);
                    }
                }, 100);
            }
        } else {
            console.error(`Component ${className} has no render method`);
            container.innerHTML = '<p style="color: #666; padding: 20px;">Component render error</p>';
        }
        
    } catch (error) {
        console.error(`Error loading ${componentName}:`, error);
        container.innerHTML = '<p style="color: #dc2626; padding: 20px;">Error loading component</p>';
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
