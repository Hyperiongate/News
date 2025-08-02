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
            body: JSON.stringify({ 
                url: url,
                pro: true  // Include pro parameter as backend expects it
            })
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
    
    // Create analysis cards with error handling
    const cards = [
        {
            title: '📊 Bias Analysis',
            icon: '📊',
            renderer: () => renderBiasAnalysis(data.bias_analysis || {})
        },
        {
            title: '✓ Fact Checking',
            icon: '✓',
            renderer: () => renderFactChecking(data.fact_check_results || {})
        },
        {
            title: '🔍 Transparency',
            icon: '🔍',
            renderer: () => renderTransparency(data.transparency_analysis || {})
        },
        {
            title: '👤 Author Analysis',
            icon: '👤',
            renderer: () => renderAuthor(data.author_analysis || {}, data.article || {})
        },
        {
            title: '📝 Article Context',
            icon: '📝',
            renderer: () => renderContext(data.article || {})
        },
        {
            title: '📖 Readability',
            icon: '📖',
            renderer: () => renderReadability(data.readability_analysis || {})
        },
        {
            title: '💭 Emotional Tone',
            icon: '💭',
            renderer: () => renderEmotionalTone(data.bias_analysis || {})
        },
        {
            title: '🏢 Source Credibility',
            icon: '🏢',
            renderer: () => renderSourceCredibility(data.source_credibility || {})
        }
    ];
    
    cards.forEach((card, index) => {
        try {
            const content = card.renderer();
            const cardEl = createCard(card.title, card.icon, content, index < 4);
            container.appendChild(cardEl);
        } catch (error) {
            console.error(`Error rendering ${card.title}:`, error);
            // Create error card
            const errorContent = `
                <p style="color: #ef4444;">Error loading this section</p>
                <p style="color: #6b7280; font-size: 14px; margin-top: 10px;">
                    ${error.message || 'Unknown error occurred'}
                </p>
            `;
            const cardEl = createCard(card.title, card.icon, errorContent, index < 4);
            container.appendChild(cardEl);
        }
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
        <div class="card-header">
            <div>
                <h4><span class="card-icon">${icon}</span> ${title}</h4>
            </div>
            <button class="expand-btn" onclick="toggleCard(this)">
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

// Toggle card expansion - global function
function toggleCard(button) {
    const card = button.closest('.analysis-card');
    if (card) {
        card.classList.toggle('expanded');
    }
}

// Make toggleCard globally available
window.toggleCard = toggleCard;

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
            ${claims.map(claim => {
                // Handle both string claims and object claims
                const claimText = typeof claim === 'string' ? claim : (claim.claim || 'Unknown claim');
                const verdict = claim.verdict || '';
                
                // Safe verdict display - ensure it's a string before calling toLowerCase
                let verdictBadge = '';
                if (verdict && typeof verdict === 'string') {
                    verdictBadge = `
                        <div class="fact-check-verdict">
                            <span class="status-badge ${verdict.toLowerCase()}">${verdict}</span>
                        </div>
                    `;
                }
                
                return `
                    <div class="fact-check-item">
                        <div class="fact-check-claim">${claimText}</div>
                        ${verdictBadge}
                    </div>
                `;
            }).join('')}
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
                    <span class="metric-value">${value === true ? '✓' : value === false ? '✗' : value}</span>
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
    
    // Safe charAt handling - ensure authorName is never empty
    const avatarLetter = authorName && authorName.length > 0 ? authorName.charAt(0).toUpperCase() : '?';
    
    // Handle verification_status as an object (which it is from the backend)
    const verificationStatus = author.verification_status || {};
    const isVerified = verificationStatus.verified || false;
    const isJournalistVerified = verificationStatus.journalist_verified || false;
    const isOutletStaff = verificationStatus.outlet_staff || false;
    
    // Determine overall verification status
    let verificationBadge = '';
    if (isVerified || isJournalistVerified || isOutletStaff) {
        const badges = [];
        if (isVerified) badges.push('Verified');
        if (isJournalistVerified) badges.push('Journalist');
        if (isOutletStaff) badges.push('Staff');
        
        verificationBadge = `
            <div class="metric-item">
                <span class="metric-label">Verification</span>
                <span class="status-badge verified">${badges.join(' • ')}</span>
            </div>
        `;
    }
    
    return `
        <div class="author-details">
            <div class="author-avatar">${avatarLetter}</div>
            <div class="author-info">
                <div class="author-name">${authorName}</div>
                <div class="author-bio">
                    ${found ? 'Found in journalist database' : 'Author not found in database'}
                    ${author.bio && author.bio !== authorName ? `: ${author.bio}` : ''}
                </div>
            </div>
        </div>
        
        <div class="metric-item" style="margin-top: 20px;">
            <span class="metric-label">Credibility Score</span>
            <span class="metric-value">${credibilityScore}/100</span>
        </div>
        
        ${verificationBadge}
        
        ${author.professional_info && author.professional_info.outlets && author.professional_info.outlets.length > 0 ? `
            <div class="metric-item">
                <span class="metric-label">Outlets</span>
                <span class="metric-value">${author.professional_info.outlets.join(', ')}</span>
            </div>
        ` : ''}
        
        ${author.credibility_explanation ? `
            <div style="margin-top: 20px; padding: 15px; background: #f9fafb; border-radius: 8px;">
                <h5 style="margin: 0 0 10px 0; color: #4b5563;">Assessment</h5>
                <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.5;">
                    ${author.credibility_explanation.explanation || ''}
                </p>
                ${author.credibility_explanation.advice ? `
                    <p style="margin: 10px 0 0 0; color: #4b5563; font-weight: 500; font-size: 14px;">
                        💡 ${author.credibility_explanation.advice}
                    </p>
                ` : ''}
            </div>
        ` : ''}
    `;
}

function renderContext(article) {
    const title = article.title || 'N/A';
    const domain = article.domain || 'N/A';
    const publishedDate = article.published_date || article.publish_date || null;
    const wordCount = article.word_count || null;
    const topics = article.topics || [];
    
    return `
        <div class="metric-item">
            <span class="metric-label">Title</span>
            <span class="metric-value" style="text-align: right; max-width: 60%;">${title}</span>
        </div>
        
        <div class="metric-item">
            <span class="metric-label">Domain</span>
            <span class="metric-value">${domain}</span>
        </div>
        
        <div class="metric-item">
            <span class="metric-label">Published</span>
            <span class="metric-value">${publishedDate ? new Date(publishedDate).toLocaleDateString() : 'N/A'}</span>
        </div>
        
        ${wordCount ? `
            <div class="metric-item">
                <span class="metric-label">Word Count</span>
                <span class="metric-value">${wordCount}</span>
            </div>
        ` : ''}
        
        ${topics.length > 0 ? `
            <h5 style="margin-top: 20px;">Topics</h5>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px;">
                ${topics.map(topic => `
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
    
    // Check if we have any emotional tone data
    const hasEmotionalData = Object.keys(emotionalTone).length > 0;
    
    return `
        ${hasEmotionalData ? `
            <h5>Detected Emotions</h5>
            ${Object.entries(emotionalTone).map(([emotion, score]) => {
                // Ensure score is a number
                const numScore = typeof score === 'number' ? score : 0;
                return `
                    <div class="metric-item">
                        <span class="metric-label">${formatLabel(emotion)}</span>
                        <div style="flex: 1; margin: 0 10px;">
                            <div class="progress-bar" style="height: 6px;">
                                <div class="progress-fill ${getEmotionClass(numScore)}" style="width: ${numScore}%"></div>
                            </div>
                        </div>
                        <span class="metric-value">${numScore}%</span>
                    </div>
                `;
            }).join('')}
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
