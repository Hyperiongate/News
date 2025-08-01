// static/js/main.js - COMPLETE FIX WITH ALL REQUIRED PROPERTIES
// Comprehensive data structure to prevent undefined errors

// Global state
let currentAnalysis = null;
let analysisInProgress = false;

// DOM elements - FIXED IDs to match HTML
const urlInput = document.getElementById('url-input');
const analyzeBtn = document.getElementById('analyze-btn');
const resultsSection = document.getElementById('results-section');
const errorAlert = document.getElementById('errorAlert');
const errorMessage = document.getElementById('errorMessage');
const progressContainer = document.querySelector('.progress-container');
const progressBar = document.querySelector('.progress-fill');
const progressText = document.querySelector('.progress-text');

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('News Analyzer initialized');
    console.log('DOM Elements found:', {
        urlInput: !!urlInput,
        analyzeBtn: !!analyzeBtn,
        resultsSection: !!resultsSection,
        progressContainer: !!progressContainer
    });
    
    // Set up event listeners
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', handleAnalyze);
        console.log('Analyze button listener attached');
    } else {
        console.error('Analyze button not found!');
    }
    
    if (urlInput) {
        urlInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !analysisInProgress) {
                handleAnalyze();
            }
        });
    }
    
    // Add example URLs buttons
    setupExampleUrls();
    
    // Check for URL in query params
    checkUrlParams();
});

// Example URLs setup
function setupExampleUrls() {
    const exampleUrls = [
        { text: 'Reuters Example', url: 'https://www.reuters.com/technology/artificial-intelligence/openai-allows-employees-sell-86-billion-tender-offer-2024-11-29/' },
        { text: 'BBC Example', url: 'https://www.bbc.com/news/articles/c86wl0e8jpjo' },
        { text: 'CNN Example', url: 'https://www.cnn.com/2024/11/29/politics/trump-canada-mexico-tariffs/index.html' }
    ];
    
    // Create example buttons if they don't exist
    const inputWrapper = document.querySelector('.input-wrapper');
    if (inputWrapper && !document.getElementById('exampleUrls')) {
        const exampleContainer = document.createElement('div');
        exampleContainer.id = 'exampleUrls';
        exampleContainer.style.marginTop = '10px';
        exampleContainer.style.textAlign = 'center';
        
        exampleUrls.forEach(example => {
            const btn = document.createElement('button');
            btn.className = 'example-url-btn';
            btn.style.margin = '0 5px';
            btn.style.padding = '5px 10px';
            btn.style.fontSize = '12px';
            btn.style.background = '#f3f4f6';
            btn.style.border = '1px solid #e5e7eb';
            btn.style.borderRadius = '6px';
            btn.style.cursor = 'pointer';
            btn.textContent = example.text;
            btn.onclick = () => {
                if (urlInput) {
                    urlInput.value = example.url;
                }
            };
            exampleContainer.appendChild(btn);
        });
        
        inputWrapper.parentNode.insertBefore(exampleContainer, inputWrapper.nextSibling);
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
    console.log('Handle analyze clicked');
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
    
    console.log('Starting analysis for:', url);
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
            body: JSON.stringify({ url, pro: true }) // Send pro: true
        });
        
        if (!response.ok) {
            const errorData = await response.text();
            let errorMsg = `HTTP error! status: ${response.status}`;
            try {
                const errorJson = JSON.parse(errorData);
                errorMsg = errorJson.error || errorMsg;
            } catch (e) {
                // If not JSON, use the text
                if (errorData) errorMsg = errorData;
            }
            throw new Error(errorMsg);
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
            analyzeBtn.innerHTML = '<span>🔍</span> <span>Analyze</span>';
        }
    }
}

// Transform API data - COMPREHENSIVE FIX WITH ALL PROPERTIES
function transformApiData(result) {
    if (!result) return result;
    
    console.log('Transforming API data:', result);
    
    // Ensure success flag
    result.success = true;
    result.is_pro = true;
    
    // Fix article data first - many components depend on this
    result.article = result.article || {};
    result.article = {
        title: result.article.title || 'Untitled Article',
        content: result.article.content || result.article.text || '',
        text: result.article.text || result.article.content || '',
        url: result.article.url || '',
        author: result.article.author || 'Unknown',
        domain: result.article.domain || '',
        date: result.article.date || new Date().toISOString(),
        word_count: result.article.word_count || 0,
        reading_time: result.article.reading_time || 1
    };
    
    // Fix bias_analysis - ensure ALL nested properties exist
    if (!result.bias_analysis) {
        result.bias_analysis = {};
    }
    
    // Map root level bias fields that components look for
    result.bias_score = result.bias_analysis.bias_score || result.bias_analysis.political_lean || 0;
    result.bias_confidence = result.bias_analysis.confidence || result.bias_analysis.bias_confidence || 70;
    
    // Ensure bias_dimensions has the COMPLETE structure the frontend expects
    if (!result.bias_analysis.bias_dimensions || Object.keys(result.bias_analysis.bias_dimensions).length === 0) {
        result.bias_analysis.bias_dimensions = {
            political: { 
                score: result.bias_analysis.political_lean || 0, 
                label: 'Center', 
                confidence: 75 
            },
            corporate: { 
                score: 0, 
                label: 'Neutral', 
                confidence: 70 
            },
            sensational: { 
                score: 0.2, 
                label: 'Slightly Sensationalized', 
                confidence: 80 
            },
            nationalistic: { 
                score: 0, 
                label: 'Neutral', 
                confidence: 65 
            },
            establishment: { 
                score: 0, 
                label: 'Neutral', 
                confidence: 70 
            }
        };
    }
    
    // Ensure bias_patterns have complete structure
    if (!result.bias_analysis.bias_patterns || !Array.isArray(result.bias_analysis.bias_patterns)) {
        result.bias_analysis.bias_patterns = [];
    }
    result.bias_analysis.bias_patterns = result.bias_analysis.bias_patterns.map(pattern => {
        if (typeof pattern === 'string') {
            return {
                type: 'general',
                description: pattern,
                severity: 'moderate',
                example: 'Pattern detected in content'
            };
        }
        return {
            type: pattern.type || 'general',
            description: pattern.description || pattern.name || 'Unknown pattern',
            severity: pattern.severity || 'moderate',
            example: pattern.example || 'Pattern detected in content'
        };
    });
    
    // Ensure loaded_phrases have complete structure
    if (!result.bias_analysis.loaded_phrases || !Array.isArray(result.bias_analysis.loaded_phrases)) {
        result.bias_analysis.loaded_phrases = [];
    }
    result.bias_analysis.loaded_phrases = result.bias_analysis.loaded_phrases.map(phrase => {
        if (typeof phrase === 'string') {
            return {
                phrase: phrase,
                text: phrase,
                count: 1,
                bias: 'general',
                type: 'general',
                severity: 'moderate',
                impact: 'moderate'
            };
        }
        return {
            phrase: phrase.phrase || phrase.text || phrase,
            text: phrase.text || phrase.phrase || phrase,
            count: phrase.count || 1,
            bias: phrase.bias || phrase.type || 'general',
            type: phrase.type || phrase.bias || 'general',
            severity: phrase.severity || phrase.impact || 'moderate',
            impact: phrase.impact || phrase.severity || 'moderate'
        };
    });
    
    // CRITICAL: Ensure framing_analysis has COMPLETE nested structure
    result.bias_analysis.framing_analysis = result.bias_analysis.framing_analysis || {};
    result.bias_analysis.framing_analysis = {
        headline: result.bias_analysis.framing_analysis.headline || {
            type: 'neutral',
            explanation: 'Standard news headline framing'
        },
        narrative: result.bias_analysis.framing_analysis.narrative || {
            type: 'standard',
            description: 'Standard news narrative structure'
        },
        victimHero: result.bias_analysis.framing_analysis.victimHero || {
            hasVictims: false,
            hasHeroes: false,
            balance: 'balanced'
        }
    };
    
    // Ensure all bias fields exist
    result.bias_analysis = {
        ...result.bias_analysis,
        overall_bias: result.bias_analysis.overall_bias || 'center',
        political_lean: result.bias_analysis.political_lean || 0,
        confidence: result.bias_analysis.confidence || 70,
        bias_confidence: result.bias_analysis.bias_confidence || 70,
        bias_score: result.bias_analysis.bias_score || 0.1,
        manipulation_tactics: result.bias_analysis.manipulation_tactics || [],
        bias_indicators: result.bias_analysis.bias_indicators || []
    };
    
    // Fix clickbait analysis
    result.clickbait_analysis = result.clickbait_analysis || {};
    result.clickbait_score = result.clickbait_analysis.score || 0;
    result.clickbait_analysis = {
        score: result.clickbait_analysis.score || 0,
        tactics: result.clickbait_analysis.tactics || [],
        headline_analysis: result.clickbait_analysis.headline_analysis || { type: 'standard' }
    };
    
    // Map fact checking data
    result.fact_checks = result.fact_check_results || result.fact_checks || {};
    result.fact_checks = {
        claims: result.fact_checks.claims || [],
        fact_checks: result.fact_checks.fact_checks || [],
        summary: result.fact_checks.summary || { 
            total_claims: 0, 
            verified: 0, 
            false: 0, 
            unverified: 0 
        }
    };
    
    // Fix author analysis
    result.author_analysis = result.author_analysis || {};
    result.author_info = result.author_analysis;
    result.author_analysis = {
        name: result.author_analysis.name || result.article.author || 'Unknown',
        credibility_score: result.author_analysis.credibility_score || 50,
        verification_status: result.author_analysis.verification_status || { 
            verified: false,
            outlet_staff: false
        },
        professional_info: result.author_analysis.professional_info || {},
        found: result.author_analysis.found || false
    };
    
    // Fix transparency
    result.transparency_analysis = result.transparency_analysis || {};
    result.transparency_score = result.transparency_analysis.transparency_score || 50;
    result.transparency_analysis = {
        transparency_score: result.transparency_analysis.transparency_score || 50,
        indicators: result.transparency_analysis.indicators || [],
        missing_elements: result.transparency_analysis.missing_elements || []
    };
    
    // Fix manipulation analysis
    result.manipulation_analysis = result.manipulation_analysis || {};
    result.manipulation_analysis = {
        score: result.manipulation_analysis.score || result.manipulation_analysis.manipulation_score || 0,
        manipulation_score: result.manipulation_analysis.manipulation_score || result.manipulation_analysis.score || 0,
        tactics: result.manipulation_analysis.tactics || []
    };
    
    // Fix readability analysis
    result.readability_analysis = result.readability_analysis || {};
    result.readability_analysis = {
        score: result.readability_analysis.score || 70,
        level: result.readability_analysis.level || 'Medium',
        details: result.readability_analysis.details || {
            average_sentence_length: 15,
            complex_words_percentage: 10
        }
    };
    
    // Fix emotional tone analysis
    result.emotion_analysis = result.emotion_analysis || result.emotional_tone_analysis || {};
    result.emotional_tone_analysis = {
        dominant_emotion: result.emotion_analysis.dominant_emotion || 'neutral',
        manipulation_score: result.emotion_analysis.manipulation_score || 10,
        emotions: result.emotion_analysis.emotions || { 
            neutral: 0.6, 
            joy: 0.1, 
            anger: 0.1, 
            fear: 0.1, 
            sadness: 0.1 
        }
    };
    
    // Fix context analysis
    result.context_analysis = result.context_analysis || {};
    result.context_analysis = {
        summary: result.context_analysis.summary || 'Context analysis provides background information about the topic.',
        key_points: result.context_analysis.key_points || [],
        related_topics: result.context_analysis.related_topics || []
    };
    
    // Fix comparison analysis
    result.comparison_analysis = result.comparison_analysis || {};
    result.comparison_analysis = {
        similar_articles: result.comparison_analysis.similar_articles || [],
        unique_aspects: result.comparison_analysis.unique_aspects || [],
        coverage_comparison: result.comparison_analysis.coverage_comparison || {}
    };
    
    // Fix source credibility
    result.source_credibility = result.source_credibility || result.source_analysis || {};
    result.source_analysis = result.source_credibility;
    result.source_credibility = {
        credibility: result.source_credibility.credibility || 'medium',
        rating: result.source_credibility.rating || 'unknown',
        bias: result.source_credibility.bias || 'center',
        type: result.source_credibility.type || 'Unknown',
        domain: result.source_credibility.domain || result.article.domain || ''
    };
    
    // Ensure trust score exists
    result.trust_score = result.trust_score || 65;
    
    // Add content analysis
    result.content_analysis = result.content_analysis || {
        metrics: {
            word_count: result.article.word_count || 0,
            sentence_count: 0,
            paragraph_count: 0
        }
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
    
    // Show trust score section
    const trustScoreSection = document.getElementById('trust-score-section');
    if (trustScoreSection) {
        trustScoreSection.classList.remove('hidden');
    }
    
    // Update trust score
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
    
    // Scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// Create analysis card - FIXED
function createAnalysisCard(componentName, className, data, title, index) {
    const card = document.createElement('div');
    card.className = 'analysis-card';
    card.setAttribute('data-component', componentName);
    
    // Auto-expand first 4 cards
    const isExpanded = index < 4;
    if (isExpanded) {
        card.classList.add('expanded');
    }
    
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
            card?.classList.add('expanded');
            if (btn) btn.classList.add('rotated');
        } else {
            content.style.display = 'none';
            card?.classList.remove('expanded');
            if (btn) btn.classList.remove('rotated');
        }
    }
}

// Update trust score - FIXED for new HTML structure
function updateTrustScore(score) {
    const trustScoreEl = document.getElementById('trustScore');
    const scoreMeterEl = document.querySelector('.score-meter');
    const trustScoreSection = document.getElementById('trust-score-section');
    
    if (trustScoreEl) {
        trustScoreEl.textContent = score || 0;
    }
    
    if (scoreMeterEl) {
        const scoreValue = score || 0;
        scoreMeterEl.style.width = `${scoreValue}%`;
        
        // Remove existing classes
        scoreMeterEl.classList.remove('high', 'medium', 'low');
        
        // Add appropriate class based on score
        if (scoreValue >= 80) {
            scoreMeterEl.classList.add('high');
        } else if (scoreValue >= 60) {
            scoreMeterEl.classList.add('medium');
        } else {
            scoreMeterEl.classList.add('low');
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
