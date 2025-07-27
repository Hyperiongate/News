// analysis-cards.js - Fixed version with proper author card display
document.addEventListener('DOMContentLoaded', function() {
    console.log('Analysis Cards: Initializing...');
    
    // Subscribe to data updates from DataManager
    if (window.dataManager) {
        window.dataManager.subscribe('analysis-cards', (data) => {
            console.log('Analysis Cards: Received data update', data);
            renderAllCards(data);
        });
        console.log('Analysis Cards: Subscribed to DataManager');
    } else {
        console.error('Analysis Cards: DataManager not found!');
    }
});

function renderAllCards(data) {
    console.log('=== RENDER ALL CARDS ===');
    console.log('Data received:', data);
    console.log('Has author_analysis:', !!data.author_analysis);
    if (data.author_analysis) {
        console.log('Author analysis details:', data.author_analysis);
    }
    
    const container = document.getElementById('analysis-cards-container');
    if (!container) {
        console.error('Analysis Cards: Container not found!');
        return;
    }
    
    // Clear existing cards
    container.innerHTML = '';
    
    // Create card structure
    const cardsHTML = `
        <div class="row g-4">
            <!-- Trust Score Card -->
            <div class="col-md-6">
                <div id="trust-score-card" class="analysis-card"></div>
            </div>
            
            <!-- Bias Analysis Card -->
            <div class="col-md-6">
                <div id="bias-analysis-card" class="analysis-card"></div>
            </div>
            
            <!-- Fact Check Card -->
            <div class="col-md-6">
                <div id="fact-check-card" class="analysis-card"></div>
            </div>
            
            <!-- Author Info Card -->
            <div class="col-md-6">
                <div id="author-info-card" class="analysis-card"></div>
            </div>
            
            <!-- Manipulation Card -->
            <div class="col-md-6">
                <div id="manipulation-card" class="analysis-card"></div>
            </div>
            
            <!-- Source Analysis Card -->
            <div class="col-md-6">
                <div id="source-analysis-card" class="analysis-card"></div>
            </div>
            
            <!-- Transparency Card -->
            <div class="col-md-6">
                <div id="transparency-card" class="analysis-card"></div>
            </div>
            
            <!-- Clickbait Card -->
            <div class="col-md-6">
                <div id="clickbait-card" class="analysis-card"></div>
            </div>
        </div>
    `;
    
    container.innerHTML = cardsHTML;
    
    // Render individual cards
    try {
        if (data.trust_score !== undefined) {
            console.log('Rendering trust score card');
            renderTrustScoreCard(data.trust_score, data);
        }
        
        if (data.bias_analysis) {
            console.log('Rendering bias analysis card');
            renderBiasAnalysisCard(data.bias_analysis);
        }
        
        if (data.fact_check !== undefined || data.fact_checks !== undefined) {
            console.log('Rendering fact check card');
            renderFactCheckCard(data.fact_check || { claims_found: data.fact_checks?.length || 0, fact_checks: data.fact_checks });
        }
        
        // CRITICAL: Render author card with proper data
        console.log('About to render author card...');
        console.log('Author data available:', data.author_analysis || data.article?.author);
        renderAuthorCard(data);
        
        if (data.manipulation_analysis || data.persuasion_analysis) {
            console.log('Rendering manipulation card');
            renderManipulationCard(data.manipulation_analysis || data.persuasion_analysis);
        }
        
        if (data.source_analysis || data.source_credibility) {
            console.log('Rendering source card');
            renderSourceCard(data.source_analysis || data.source_credibility);
        }
        
        if (data.transparency_score || data.transparency_analysis) {
            console.log('Rendering transparency card');
            renderTransparencyCard(data.transparency_score || data.transparency_analysis);
        }
        
        if (data.clickbait_analysis || data.clickbait_score !== undefined) {
            console.log('Rendering clickbait card');
            renderClickbaitCard(data.clickbait_analysis || { score: data.clickbait_score });
        }
    } catch (error) {
        console.error('Error rendering cards:', error);
    }
}

function renderTrustScoreCard(trustScore, fullData) {
    const card = document.getElementById('trust-score-card');
    if (!card) return;
    
    const score = typeof trustScore === 'object' ? (trustScore.score || 0) : trustScore;
    const interpretation = typeof trustScore === 'object' ? trustScore.interpretation : getInterpretation(score);
    const factors = typeof trustScore === 'object' && trustScore.factors ? trustScore.factors : calculateFactors(fullData);
    
    const badgeClass = score >= 80 ? 'success' : score >= 60 ? 'warning' : 'danger';
    const badgeText = score >= 80 ? 'Trusted' : score >= 60 ? 'Mixed' : 'Caution';
    
    card.innerHTML = `
        <div class="card h-100 border-primary">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">
                    <i class="bi bi-shield-check"></i> Trust Score
                    <span class="badge bg-${badgeClass} float-end">${badgeText}</span>
                </h5>
            </div>
            <div class="card-body">
                <div class="text-center mb-4">
                    <div class="trust-meter">
                        <svg viewBox="0 0 200 200" width="150" height="150">
                            <circle cx="100" cy="100" r="90" fill="none" stroke="#e0e0e0" stroke-width="20"/>
                            <circle cx="100" cy="100" r="90" fill="none" stroke="#0d6efd" stroke-width="20"
                                    stroke-dasharray="${score * 5.65} 565.48"
                                    stroke-dashoffset="0"
                                    transform="rotate(-90 100 100)"/>
                            <text x="100" y="100" text-anchor="middle" dominant-baseline="middle" 
                                  font-size="48" font-weight="bold" fill="#0d6efd">${score}</text>
                            <text x="100" y="130" text-anchor="middle" font-size="16" fill="#666">${interpretation}</text>
                        </svg>
                    </div>
                </div>
                
                ${factors ? `
                    <h6 class="mb-3">Score Breakdown:</h6>
                    <div class="score-factors">
                        ${Object.entries(factors).map(([key, value]) => `
                            <div class="d-flex justify-content-between mb-2">
                                <span>${formatFactorName(key)}:</span>
                                <span class="badge bg-secondary">${value}%</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

function renderBiasAnalysisCard(biasData) {
    const card = document.getElementById('bias-analysis-card');
    if (!card) return;
    
    const politicalBias = biasData.political_bias || {};
    const corporateBias = biasData.corporate_bias || {};
    const sensationalism = biasData.sensationalism || biasData.sensational_bias?.score || 0;
    const politicalLean = biasData.political_lean || politicalBias.score || 0;
    
    card.innerHTML = `
        <div class="card h-100 border-warning">
            <div class="card-header bg-warning text-dark">
                <h5 class="mb-0">
                    <i class="bi bi-balance-scale"></i> Bias Analysis
                </h5>
            </div>
            <div class="card-body">
                <div class="bias-section mb-4">
                    <h6>Political Bias</h6>
                    <div class="bias-scale">
                        <div class="scale-labels d-flex justify-content-between text-muted small">
                            <span>Far Left</span>
                            <span>Center</span>
                            <span>Far Right</span>
                        </div>
                        <div class="progress" style="height: 25px;">
                            <div class="progress-bar bg-primary" 
                                 style="width: ${calculateBiasPosition(politicalLean)}%">
                                <span class="position-indicator">●</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                ${corporateBias.score !== undefined ? `
                    <div class="bias-section mb-4">
                        <h6>Corporate Bias</h6>
                        <div class="progress">
                            <div class="progress-bar bg-info" style="width: ${corporateBias.score || 0}%">
                                ${corporateBias.score || 0}%
                            </div>
                        </div>
                    </div>
                ` : ''}
                
                <div class="bias-section">
                    <h6>Sensationalism</h6>
                    <div class="progress">
                        <div class="progress-bar bg-danger" style="width: ${sensationalism}%">
                            ${sensationalism}%
                        </div>
                    </div>
                </div>
                
                ${biasData.framing_bias || biasData.overall_bias ? `
                    <div class="mt-3 p-3 bg-light rounded">
                        <h6>Analysis Summary</h6>
                        <p class="mb-0 small">${biasData.framing_bias || `Overall bias level: ${biasData.overall_bias}`}</p>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

function renderFactCheckCard(factData) {
    const card = document.getElementById('fact-check-card');
    if (!card) return;
    
    const totalClaims = factData.claims_found || factData.fact_checks?.length || 0;
    const verified = factData.verified || 0;
    const unverified = factData.unverified || (totalClaims - verified);
    const falseClaims = factData.false || 0;
    const claims = factData.fact_checks || factData.claims || [];
    
    card.innerHTML = `
        <div class="card h-100 border-success">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0">
                    <i class="bi bi-check-circle"></i> Fact Check
                </h5>
            </div>
            <div class="card-body">
                <div class="fact-stats mb-4">
                    <div class="row text-center">
                        <div class="col-4">
                            <h3 class="text-success">${verified}</h3>
                            <small class="text-muted">Verified</small>
                        </div>
                        <div class="col-4">
                            <h3 class="text-warning">${unverified}</h3>
                            <small class="text-muted">Unverified</small>
                        </div>
                        <div class="col-4">
                            <h3 class="text-danger">${falseClaims}</h3>
                            <small class="text-muted">False</small>
                        </div>
                    </div>
                </div>
                
                ${claims.length > 0 ? `
                    <div class="claims-list">
                        <h6>Key Claims:</h6>
                        <ul class="list-unstyled">
                            ${claims.slice(0, 3).map(claim => `
                                <li class="mb-2">
                                    <span class="badge bg-${getClaimStatusColor(claim.rating || claim.status || 'unverified')} me-2">
                                        ${claim.rating || claim.status || 'unverified'}
                                    </span>
                                    <small>${claim.claim || claim.text || 'Claim text'}</small>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : '<p class="text-muted">No specific claims analyzed</p>'}
            </div>
        </div>
    `;
}

function renderAuthorCard(data) {
    const card = document.getElementById('author-info-card');
    if (!card) {
        console.error('Author card element not found!');
        return;
    }
    
    console.log('=== RENDERING AUTHOR CARD ===');
    console.log('Full data object:', data);
    console.log('data.author_analysis:', data.author_analysis);
    console.log('data.article:', data.article);
    
    // Try multiple sources for author data
    const authorData = data.author_analysis || {};
    const authorName = authorData.name || data.article?.author || 'Unknown Author';
    const credibilityScore = authorData.credibility_score || 0;
    const bio = authorData.bio || '';
    const found = authorData.found || false;
    const expertise = authorData.expertise || authorData.professional_info?.expertise_areas || [];
    
    console.log('Author name:', authorName);
    console.log('Credibility score:', credibilityScore);
    console.log('Found:', found);
    
    card.innerHTML = `
        <div class="card h-100 border-info">
            <div class="card-header bg-info text-white">
                <h5 class="mb-0">
                    <i class="bi bi-person-badge"></i> Author Analysis
                </h5>
            </div>
            <div class="card-body">
                <div class="author-header mb-3">
                    <h6>${authorName}</h6>
                    ${found ? `
                        <div class="credibility-score">
                            <span class="badge bg-${getCredibilityColor(credibilityScore)} fs-6">
                                Credibility: ${credibilityScore}/100
                            </span>
                        </div>
                    ` : `
                        <div class="alert alert-warning mb-0">
                            <small>Limited author information available</small>
                        </div>
                    `}
                </div>
                
                ${bio ? `
                    <div class="author-bio mb-3">
                        <p class="small text-muted">${bio}</p>
                    </div>
                ` : ''}
                
                ${expertise.length > 0 ? `
                    <div class="expertise">
                        <h6>Areas of Expertise:</h6>
                        <div class="expertise-tags">
                            ${expertise.map(area => `
                                <span class="badge bg-secondary me-1 mb-1">${area}</span>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${authorData.professional_info ? `
                    <div class="professional-info mt-3">
                        ${authorData.professional_info.current_position ? `
                            <p class="mb-1"><strong>Position:</strong> ${authorData.professional_info.current_position}</p>
                        ` : ''}
                        ${authorData.professional_info.years_experience ? `
                            <p class="mb-1"><strong>Experience:</strong> ${authorData.professional_info.years_experience} years</p>
                        ` : ''}
                    </div>
                ` : ''}
                
                ${authorData.verification_status ? `
                    <div class="verification-badges mt-3">
                        ${authorData.verification_status.verified ? '<span class="badge bg-success me-1">✓ Verified</span>' : ''}
                        ${authorData.verification_status.journalist_verified ? '<span class="badge bg-primary me-1">📰 Journalist</span>' : ''}
                    </div>
                ` : ''}
                
                <div class="mt-3">
                    <button class="btn btn-sm btn-outline-info w-100" 
                            onclick="showFullAuthorProfile('${authorName.replace(/'/g, "\\'")}')">
                        View Complete Profile
                    </button>
                </div>
            </div>
        </div>
    `;
    
    console.log('Author card HTML set');
}

function renderManipulationCard(manipData) {
    const card = document.getElementById('manipulation-card');
    if (!card) return;
    
    const score = manipData.score || manipData.persuasion_score || 0;
    const tactics = manipData.tactics_found || manipData.tactics || [];
    const severity = manipData.severity || (score > 70 ? 'high' : score > 40 ? 'medium' : 'low');
    
    const severityColor = severity === 'high' ? 'danger' : severity === 'medium' ? 'warning' : 'success';
    
    card.innerHTML = `
        <div class="card h-100 border-danger">
            <div class="card-header bg-danger text-white">
                <h5 class="mb-0">
                    <i class="bi bi-exclamation-triangle"></i> Manipulation Detection
                </h5>
            </div>
            <div class="card-body">
                <div class="text-center mb-3">
                    <h2 class="text-${severityColor}">${score}%</h2>
                    <span class="badge bg-${severityColor}">${severity.toUpperCase()} Risk</span>
                </div>
                
                ${tactics.length > 0 ? `
                    <div class="tactics-found">
                        <h6>Tactics Detected:</h6>
                        <ul class="list-unstyled">
                            ${tactics.map(tactic => `
                                <li class="mb-2">
                                    <i class="bi bi-exclamation-circle text-warning"></i>
                                    <span class="ms-2">${typeof tactic === 'string' ? tactic : tactic.name}</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : '<p class="text-muted">No manipulation tactics detected</p>'}
            </div>
        </div>
    `;
}

function renderSourceCard(sourceData) {
    const card = document.getElementById('source-analysis-card');
    if (!card) return;
    
    const credibility = sourceData.credibility || sourceData.rating || 'unknown';
    const biasRating = sourceData.bias_rating || sourceData.bias || 'unknown';
    const factualReporting = sourceData.factual_reporting || 'unknown';
    const mediaType = sourceData.media_type || sourceData.type || 'unknown';
    
    card.innerHTML = `
        <div class="card h-100 border-secondary">
            <div class="card-header bg-secondary text-white">
                <h5 class="mb-0">
                    <i class="bi bi-newspaper"></i> Source Analysis
                </h5>
            </div>
            <div class="card-body">
                <div class="source-metrics">
                    <div class="metric mb-3">
                        <strong>Credibility:</strong>
                        <span class="badge bg-${getCredibilityBadgeColor(credibility)} ms-2">
                            ${credibility.toUpperCase()}
                        </span>
                    </div>
                    
                    <div class="metric mb-3">
                        <strong>Bias Rating:</strong>
                        <span class="badge bg-info ms-2">${biasRating.toUpperCase()}</span>
                    </div>
                    
                    <div class="metric mb-3">
                        <strong>Factual Reporting:</strong>
                        <span class="badge bg-${getFactualBadgeColor(factualReporting)} ms-2">
                            ${factualReporting.toUpperCase()}
                        </span>
                    </div>
                    
                    <div class="metric">
                        <strong>Media Type:</strong>
                        <span class="ms-2">${mediaType}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderTransparencyCard(transparencyData) {
    const card = document.getElementById('transparency-card');
    if (!card) return;
    
    const score = transparencyData.score || transparencyData.transparency_score || 0;
    const hasAuthor = transparencyData.has_author !== undefined ? transparencyData.has_author : true;
    const hasDate = transparencyData.has_date !== undefined ? transparencyData.has_date : true;
    const hasSources = transparencyData.has_sources !== undefined ? transparencyData.has_sources : false;
    const hasQuotes = transparencyData.has_quotes !== undefined ? transparencyData.has_quotes : false;
    
    card.innerHTML = `
        <div class="card h-100 border-purple">
            <div class="card-header bg-purple text-white">
                <h5 class="mb-0">
                    <i class="bi bi-eye"></i> Transparency Score
                </h5>
            </div>
            <div class="card-body">
                <div class="text-center mb-4">
                    <div class="circular-progress">
                        <svg viewBox="0 0 100 100" width="100" height="100">
                            <circle cx="50" cy="50" r="45" fill="none" stroke="#e0e0e0" stroke-width="10"/>
                            <circle cx="50" cy="50" r="45" fill="none" stroke="#6f42c1" stroke-width="10"
                                    stroke-dasharray="${score * 2.83} 283"
                                    stroke-dashoffset="0"
                                    transform="rotate(-90 50 50)"/>
                            <text x="50" y="50" text-anchor="middle" dominant-baseline="middle" 
                                  font-size="24" font-weight="bold" fill="#6f42c1">${score}%</text>
                        </svg>
                    </div>
                </div>
                
                <div class="transparency-checklist">
                    <div class="check-item ${hasAuthor ? 'checked' : ''}">
                        <i class="bi ${hasAuthor ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger'}"></i>
                        <span class="ms-2">Author Attribution</span>
                    </div>
                    <div class="check-item ${hasDate ? 'checked' : ''}">
                        <i class="bi ${hasDate ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger'}"></i>
                        <span class="ms-2">Publication Date</span>
                    </div>
                    <div class="check-item ${hasSources ? 'checked' : ''}">
                        <i class="bi ${hasSources ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger'}"></i>
                        <span class="ms-2">Sources Cited</span>
                    </div>
                    <div class="check-item ${hasQuotes ? 'checked' : ''}">
                        <i class="bi ${hasQuotes ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger'}"></i>
                        <span class="ms-2">Direct Quotes</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderClickbaitCard(clickbaitData) {
    const card = document.getElementById('clickbait-card');
    if (!card) return;
    
    const score = clickbaitData.score || clickbaitData.clickbait_score || 0;
    const level = clickbaitData.clickbait_level || (score < 30 ? 'low' : score < 60 ? 'medium' : 'high');
    const indicators = clickbaitData.indicators || [];
    
    const levelColor = level === 'high' ? 'danger' : level === 'medium' ? 'warning' : 'success';
    
    card.innerHTML = `
        <div class="card h-100 border-orange">
            <div class="card-header bg-orange text-white">
                <h5 class="mb-0">
                    <i class="bi bi-mouse"></i> Clickbait Analysis
                </h5>
            </div>
            <div class="card-body">
                <div class="clickbait-gauge text-center mb-4">
                    <div class="gauge-wrapper">
                        <svg viewBox="0 0 200 150" width="200" height="150">
                            <path d="M 30 120 A 70 70 0 0 1 170 120" fill="none" stroke="#e0e0e0" stroke-width="20"/>
                            <path d="M 30 120 A 70 70 0 0 1 ${30 + (140 * score / 100)} 120" 
                                  fill="none" stroke="#fd7e14" stroke-width="20"/>
                            <text x="100" y="100" text-anchor="middle" font-size="36" font-weight="bold" fill="#fd7e14">
                                ${score}%
                            </text>
                            <text x="100" y="130" text-anchor="middle" font-size="14" fill="#666">
                                ${level.toUpperCase()} CLICKBAIT
                            </text>
                        </svg>
                    </div>
                </div>
                
                ${indicators.length > 0 ? `
                    <div class="indicators">
                        <h6>Indicators Found:</h6>
                        <ul class="list-unstyled">
                            ${indicators.map(indicator => `
                                <li class="mb-1">
                                    <i class="bi bi-dot text-${levelColor}"></i>
                                    <small>${indicator}</small>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : '<p class="text-muted">No clickbait indicators found</p>'}
            </div>
        </div>
    `;
}

// Helper functions
function formatFactorName(factor) {
    return factor.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

function calculateBiasPosition(lean) {
    // Convert political lean (-100 to +100) to position (0 to 100)
    return 50 + (lean / 2);
}

function getClaimStatusColor(status) {
    switch(status?.toLowerCase()) {
        case 'verified':
        case 'true':
            return 'success';
        case 'unverified':
        case 'mixed':
            return 'warning';
        case 'false':
            return 'danger';
        default:
            return 'secondary';
    }
}

function getCredibilityColor(score) {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
}

function getCredibilityBadgeColor(credibility) {
    switch(credibility?.toLowerCase()) {
        case 'high': return 'success';
        case 'medium': return 'warning';
        case 'low': return 'danger';
        default: return 'secondary';
    }
}

function getFactualBadgeColor(rating) {
    switch(rating?.toLowerCase()) {
        case 'high': return 'success';
        case 'mixed': return 'warning';
        case 'low': return 'danger';
        default: return 'secondary';
    }
}

function getInterpretation(score) {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
}

function calculateFactors(data) {
    // If we don't have explicit factors, try to calculate them
    const factors = {};
    
    // Source credibility
    if (data.source_credibility || data.source_analysis) {
        const sourceData = data.source_credibility || data.source_analysis;
        factors.source_credibility = mapCredibilityToScore(sourceData.rating || sourceData.credibility);
    }
    
    // Author credibility
    if (data.author_analysis) {
        factors.author_credibility = data.author_analysis.credibility_score || 50;
    }
    
    // Transparency
    if (data.transparency_analysis || data.transparency_score) {
        const transData = data.transparency_analysis || data.transparency_score;
        factors.transparency = transData.transparency_score || transData.score || 50;
    }
    
    // Bias impact (inverse of objectivity)
    if (data.bias_analysis) {
        const objectivity = data.bias_analysis.objectivity_score || 0.5;
        factors.bias_impact = Math.round((1 - objectivity) * 100);
    }
    
    return Object.keys(factors).length > 0 ? factors : null;
}

function mapCredibilityToScore(credibility) {
    const mapping = {
        'high': 90,
        'medium': 60,
        'low': 30,
        'very low': 10,
        'unknown': 50
    };
    return mapping[credibility?.toLowerCase()] || 50;
}

function showFullAuthorProfile(authorName) {
    // This will be handled by author-info.js or a modal
    console.log('Showing full profile for:', authorName);
    
    // Try to find more detailed author info
    if (window.dataManager && window.dataManager.analysisData) {
        const authorData = window.dataManager.analysisData.author_analysis;
        if (authorData) {
            // You could open a modal here or expand the card
            alert(`Full author profile:\n\nName: ${authorData.name}\nCredibility: ${authorData.credibility_score}/100\n\n${authorData.bio || 'No biography available'}`);
        }
    }
}

// Add custom CSS for purple and orange colors
const style = document.createElement('style');
style.textContent = `
    .border-purple { border-color: #6f42c1 !important; }
    .bg-purple { background-color: #6f42c1 !important; }
    .border-orange { border-color: #fd7e14 !important; }
    .bg-orange { background-color: #fd7e14 !important; }
    .analysis-card { animation: fadeIn 0.5s ease-in; }
    .position-indicator { font-size: 20px; }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);

// Debug helper
window.debugAnalysisCards = function() {
    console.log('=== ANALYSIS CARDS DEBUG ===');
    console.log('DataManager exists:', !!window.dataManager);
    console.log('Current data:', window.dataManager?.analysisData);
    
    const container = document.getElementById('analysis-cards-container');
    console.log('Container exists:', !!container);
    
    const authorCard = document.getElementById('author-info-card');
    console.log('Author card element exists:', !!authorCard);
    if (authorCard) {
        console.log('Author card content:', authorCard.innerHTML);
    }
};
