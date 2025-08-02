// Simple News Analyzer - Clean, Working Version
// No complex components - just direct, reliable rendering

// Global state
let currentAnalysis = null;
let analysisInProgress = false;

// DOM elements
const urlInput = document.getElementById('url-input');
const analyzeBtn = document.getElementById('analyze-btn');
const resultsSection = document.getElementById('results-section');
const errorAlert = document.getElementById('errorAlert');
const errorMessage = document.getElementById('errorMessage');
const progressContainer = document.querySelector('.progress-container');
const progressBar = document.querySelector('.progress-fill');
const progressText = document.querySelector('.progress-text');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('News Analyzer Initialized');
    
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', handleAnalyze);
    }
    
    if (urlInput) {
        urlInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleAnalyze();
            }
        });
    }
});

// Handle analyze
async function handleAnalyze() {
    const url = urlInput ? urlInput.value.trim() : '';
    
    if (!url) {
        showError('Please enter a URL');
        return;
    }
    
    console.log('Analyzing:', url);
    
    // Hide any previous errors
    hideError();
    
    // Update UI
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span>🔄</span> <span>Analyzing...</span>';
    }
    
    // Show progress
    showProgress();
    
    try {
        // Make API call with correct format
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })  // Correct format
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        console.log('Analysis complete:', result);
        
        // Store globally
        currentAnalysis = result;
        window.currentAnalysis = result;  // Make available globally
        
        // Hide progress
        hideProgress();
        
        // Display results
        displayResults(result);
        
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to analyze article: ' + error.message);
        hideProgress();
    } finally {
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<span>🔍</span> <span>Analyze</span>';
        }
    }
}

// Show/hide progress
function showProgress() {
    if (progressContainer) {
        progressContainer.style.display = 'block';
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) {
                clearInterval(interval);
                progress = 90;
            }
            if (progressBar) progressBar.style.width = progress + '%';
            if (progressText) progressText.textContent = 'Analyzing article...';
        }, 500);
    }
}

function hideProgress() {
    if (progressContainer) {
        progressContainer.style.display = 'none';
        if (progressBar) progressBar.style.width = '0%';
    }
}

// Show/hide errors
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

// Display results in a clean, simple way
function displayResults(data) {
    const container = document.querySelector('.results-grid');
    if (!container) {
        console.error('No results container found');
        return;
    }
    
    // Clear previous results
    container.innerHTML = '';
    
    // Show trust score section
    const trustScoreSection = document.getElementById('trust-score-section');
    if (trustScoreSection) {
        trustScoreSection.classList.remove('hidden');
        const trustScoreEl = document.getElementById('trustScore');
        if (trustScoreEl) {
            trustScoreEl.textContent = data.trust_score || 'N/A';
        }
        
        // Update meter
        const scoreMeter = document.querySelector('.score-meter');
        if (scoreMeter && data.trust_score) {
            scoreMeter.style.width = `${data.trust_score}%`;
            scoreMeter.className = 'score-meter';
            if (data.trust_score >= 70) {
                scoreMeter.classList.add('high');
            } else if (data.trust_score >= 40) {
                scoreMeter.classList.add('medium');
            } else {
                scoreMeter.classList.add('low');
            }
        }
    }
    
    // Create analysis cards
    const cards = [
        {
            title: '📊 Bias Analysis',
            icon: '📊',
            content: renderBiasAnalysis(data.bias_analysis || {})
        },
        {
            title: '✓ Fact Checking',
            icon: '✓',
            content: renderFactChecking(data.fact_check_results || {})
        },
        {
            title: '🔍 Transparency',
            icon: '🔍',
            content: renderTransparency(data.transparency_analysis || {})
        },
        {
            title: '👤 Author Analysis',
            icon: '👤',
            content: renderAuthor(data.author_analysis || {}, data.article || {})
        },
        {
            title: '📝 Article Context',
            icon: '📝',
            content: renderContext(data.article || {})
        },
        {
            title: '📖 Readability',
            icon: '📖',
            content: renderReadability(data.readability_analysis || {})
        },
        {
            title: '💭 Emotional Tone',
            icon: '💭',
            content: renderEmotionalTone(data.bias_analysis || {})
        },
        {
            title: '🏢 Source Credibility',
            icon: '🏢',
            content: renderSourceCredibility(data.source_credibility || {})
        }
    ];
    
    cards.forEach((card, index) => {
        const cardEl = createCard(card.title, card.icon, card.content, index < 4);
        container.appendChild(cardEl);
    });
    
    // Show results section
    if (resultsSection) {
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// Create a card element
function createCard(title, icon, content, expanded = false) {
    const card = document.createElement('div');
    card.className = 'analysis-card' + (expanded ? ' expanded' : '');
    
    card.innerHTML = `
        <div class="card-header" onclick="toggleCard(this.parentElement)">
            <div>
                <h4><span class="card-icon">${icon}</span> ${title}</h4>
            </div>
            <button class="expand-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M19 9l-7 7-7-7" />
                </svg>
            </button>
        </div>
        <div class="card-content">
            ${content}
        </div>
    `;
    
    return card;
}

// Toggle card expansion
window.toggleCard = function(card) {
    card.classList.toggle('expanded');
}

// Render functions for each section
function renderBiasAnalysis(bias) {
    const biasScore = bias.bias_score || 50;
    const politicalLean = bias.political_lean || 'Unknown';
    const confidence = bias.confidence || 0;
    
    return `
        <div class="bias-meter">
            <h5>Overall Bias Score</h5>
            <div class="progress-bar" style="margin: 10px 0;">
                <div class="progress-fill ${getBiasClass(biasScore)}" style="width: ${biasScore}%"></div>
            </div>
            <p style="text-align: center; margin: 10px 0; font-weight: 600;">${biasScore}/100</p>
        </div>
        
        <div class="metric-item">
            <span class="metric-label">Political Lean</span>
            <span class="metric-value">${politicalLean}</span>
        </div>
        
        <div class="metric-item">
            <span class="metric-label">Confidence</span>
            <span class="metric-value">${confidence}%</span>
        </div>
        
        ${bias.bias_dimensions ? `
            <h5 style="margin-top: 20px;">Bias Dimensions</h5>
            ${Object.entries(bias.bias_dimensions).map(([key, value]) => `
                <div class="metric-item">
                    <span class="metric-label">${formatLabel(key)}</span>
                    <span class="metric-value">${value}/10</span>
                </div>
            `).join('')}
        ` : ''}
        
        ${bias.manipulation_tactics && bias.manipulation_tactics.length > 0 ? `
            <h5 style="margin-top: 20px;">Detected Tactics</h5>
            <ul style="margin: 10px 0;">
                ${bias.manipulation_tactics.map(tactic => `
                    <li>${tactic}</li>
                `).join('')}
            </ul>
        ` : ''}
    `;
}

function renderFactChecking(factCheck) {
    const claims = factCheck.claims || [];
    const summary = factCheck.summary || 'No fact-checking data available';
    
    return `
        <div style="margin-bottom: 15px;">
            <p style="color: #6b7280; line-height: 1.6;">${summary}</p>
        </div>
        
        ${claims.length > 0 ? `
            <h5>Claims Analyzed</h5>
            ${claims.map(claim => `
                <div class="fact-check-item">
                    <div class="fact-check-claim">${claim.claim || claim}</div>
                    ${claim.verdict ? `
                        <div class="fact-check-verdict">
                            <span class="status-badge ${claim.verdict.toLowerCase()}">${claim.verdict}</span>
                        </div>
                    ` : ''}
                </div>
            `).join('')}
        ` : '<p style="color: #6b7280;">No specific claims analyzed</p>'}
    `;
}

function renderTransparency(transparency) {
    const score = transparency.transparency_score || 0;
    const indicators = transparency.transparency_indicators || {};
    
    return `
        <div class="metric-item">
            <span class="metric-label">Transparency Score</span>
            <span class="metric-value">${score}/100</span>
        </div>
        
        ${Object.keys(indicators).length > 0 ? `
            <h5 style="margin-top: 20px;">Transparency Indicators</h5>
            ${Object.entries(indicators).map(([key, value]) => `
                <div class="metric-item">
                    <span class="metric-label">${formatLabel(key)}</span>
                    <span class="metric-value">${value ? '✓' : '✗'}</span>
                </div>
            `).join('')}
        ` : ''}
        
        ${transparency.missing_elements && transparency.missing_elements.length > 0 ? `
            <h5 style="margin-top: 20px;">Missing Elements</h5>
            <ul>
                ${transparency.missing_elements.map(element => `
                    <li>${element}</li>
                `).join('')}
            </ul>
        ` : ''}
    `;
}

function renderAuthor(author, article) {
    const authorName = author.name || article.author || 'Unknown';
    const credibilityScore = author.credibility_score || 0;
    const found = author.found || false;
    
    return `
        <div class="author-details">
            <div class="author-avatar">${authorName.charAt(0).toUpperCase()}</div>
            <div class="author-info">
                <div class="author-name">${authorName}</div>
                <div class="author-bio">
                    ${found ? 'Verified journalist' : 'Author not found in database'}
                </div>
            </div>
        </div>
        
        <div class="metric-item" style="margin-top: 20px;">
            <span class="metric-label">Credibility Score</span>
            <span class="metric-value">${credibilityScore}/100</span>
        </div>
        
        ${author.verification_status ? `
            <div class="metric-item">
                <span class="metric-label">Verification Status</span>
                <span class="status-badge ${author.verification_status.toLowerCase()}">${author.verification_status}</span>
            </div>
        ` : ''}
    `;
}

function renderContext(article) {
    return `
        <div class="metric-item">
            <span class="metric-label">Title</span>
            <span class="metric-value" style="text-align: right; max-width: 60%;">${article.title || 'N/A'}</span>
        </div>
        
        <div class="metric-item">
            <span class="metric-label">Domain</span>
            <span class="metric-value">${article.domain || 'N/A'}</span>
        </div>
        
        <div class="metric-item">
            <span class="metric-label">Published</span>
            <span class="metric-value">${article.published_date ? new Date(article.published_date).toLocaleDateString() : 'N/A'}</span>
        </div>
        
        ${article.word_count ? `
            <div class="metric-item">
                <span class="metric-label">Word Count</span>
                <span class="metric-value">${article.word_count}</span>
            </div>
        ` : ''}
        
        ${article.topics && article.topics.length > 0 ? `
            <h5 style="margin-top: 20px;">Topics</h5>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px;">
                ${article.topics.map(topic => `
                    <span class="preview-badge medium">${topic}</span>
                `).join('')}
            </div>
        ` : ''}
    `;
}

function renderReadability(readability) {
    const score = readability.readability_score || readability.score || 0;
    const level = readability.readability_level || readability.level || 'Unknown';
    
    return `
        <div class="metric-item">
            <span class="metric-label">Readability Score</span>
            <span class="metric-value">${score}/100</span>
        </div>
        
        <div class="metric-item">
            <span class="metric-label">Reading Level</span>
            <span class="metric-value">${level}</span>
        </div>
        
        ${readability.metrics ? `
            <h5 style="margin-top: 20px;">Detailed Metrics</h5>
            ${Object.entries(readability.metrics).map(([key, value]) => `
                <div class="metric-item">
                    <span class="metric-label">${formatLabel(key)}</span>
                    <span class="metric-value">${value}</span>
                </div>
            `).join('')}
        ` : ''}
    `;
}

function renderEmotionalTone(bias) {
    const emotionalTone = bias.emotional_tone || {};
    const manipulationScore = bias.emotional_manipulation_score || 0;
    
    return `
        ${Object.keys(emotionalTone).length > 0 ? `
            <h5>Detected Emotions</h5>
            ${Object.entries(emotionalTone).map(([emotion, score]) => `
                <div class="metric-item">
                    <span class="metric-label">${formatLabel(emotion)}</span>
                    <div style="flex: 1; margin: 0 10px;">
                        <div class="progress-bar" style="height: 6px;">
                            <div class="progress-fill ${getEmotionClass(score)}" style="width: ${score}%"></div>
                        </div>
                    </div>
                    <span class="metric-value">${score}%</span>
                </div>
            `).join('')}
        ` : '<p style="color: #6b7280;">No emotional tone data available</p>'}
        
        ${manipulationScore > 0 ? `
            <div class="metric-item" style="margin-top: 20px;">
                <span class="metric-label">Emotional Manipulation Score</span>
                <span class="metric-value ${manipulationScore > 50 ? 'style="color: #ef4444;"' : ''}">${manipulationScore}/100</span>
            </div>
        ` : ''}
    `;
}

function renderSourceCredibility(source) {
    const credibility = source.credibility || 'Unknown';
    const rating = source.rating || 'N/A';
    const bias = source.bias || 'Unknown';
    
    return `
        <div class="source-credibility">
            <div class="credibility-score">${rating}</div>
            <div class="credibility-label">${credibility}</div>
        </div>
        
        <div class="metric-item" style="margin-top: 20px;">
            <span class="metric-label">Political Bias</span>
            <span class="metric-value">${bias}</span>
        </div>
        
        ${source.factual_reporting ? `
            <div class="metric-item">
                <span class="metric-label">Factual Reporting</span>
                <span class="metric-value">${source.factual_reporting}</span>
            </div>
        ` : ''}
        
        ${source.methodology ? `
            <h5 style="margin-top: 20px;">Methodology</h5>
            <p style="color: #6b7280; font-size: 14px; line-height: 1.5;">${source.methodology}</p>
        ` : ''}
    `;
}

// Helper functions
function getBiasClass(score) {
    if (score >= 70) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
}

function getEmotionClass(score) {
    if (score >= 70) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
}

function formatLabel(key) {
    return key.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

console.log('News Analyzer loaded successfully');
