// analysis-cards.js - Complete Analysis Cards Component with Full Data Display - FIXED VERSION
class AnalysisCards {
    constructor() {
        this.cardTypes = ['trust', 'bias', 'facts', 'author', 'clickbait', 'source', 'manipulation', 'metrics'];
    }

    render(container, data, isPro = false) {
        if (!container || !data) {
            console.error('AnalysisCards: Missing container or data');
            return;
        }

        // Store data globally for debugging
        window.LAST_ANALYSIS_DATA = data;
        
        // Clear existing content
        container.innerHTML = '';
        
        // Create cards container
        const cardsContainer = document.createElement('div');
        cardsContainer.className = 'analysis-cards-container';
        
        // Create each card
        this.cardTypes.forEach(type => {
            const card = this.createCard(type, data, isPro);
            if (card) {
                cardsContainer.appendChild(card);
            }
        });
        
        container.appendChild(cardsContainer);
        
        // Add export section
        this.addExportSection(container, data);
    }

    createCard(type, data, isPro) {
        let card;
        
        switch(type) {
            case 'trust':
                card = this.createTrustCard(data);
                break;
            case 'bias':
                card = this.createBiasCard(data);
                break;
            case 'facts':
                card = this.createFactsCard(data, isPro);
                break;
            case 'author':
                card = this.createAuthorCard(data);
                break;
            case 'clickbait':
                card = this.createClickbaitCard(data, isPro);
                break;
            case 'source':
                card = this.createSourceCard(data);
                break;
            case 'manipulation':
                card = this.createManipulationCard(data);
                break;
            case 'metrics':
                card = this.createMetricsCard(data);
                break;
            default:
                console.warn(`Unknown card type: ${type}`);
                return null;
        }
        
        // Add collapsible functionality
        if (card) {
            this.makeCollapsible(card);
        }
        
        return card;
    }

    createTrustCard(data) {
        if (!data) return null;
        
        const trustScore = data.trust_score || 0;
        const components = data.trust_components || data.trust_score_breakdown || [];
        
        const card = document.createElement('div');
        card.className = 'analysis-card trust-card';
        
        // Determine color based on score
        let color = '#ef4444'; // red
        let label = 'Low Trust';
        if (trustScore >= 70) {
            color = '#10b981'; // green
            label = 'High Trust';
        } else if (trustScore >= 40) {
            color = '#f59e0b'; // yellow
            label = 'Medium Trust';
        }
        
        card.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">🛡️</span>
                <span>Trust Score</span>
            </div>
            
            <div class="trust-content">
                <div class="trust-score-display">
                    <svg class="trust-meter" viewBox="0 0 200 200">
                        <circle class="trust-bg" cx="100" cy="100" r="90"></circle>
                        <circle class="trust-fill" cx="100" cy="100" r="90" 
                                style="stroke: ${color}; stroke-dasharray: ${565 * (trustScore / 100)} 565;">
                        </circle>
                    </svg>
                    <div class="trust-score-text">
                        <div class="trust-score-number">${trustScore}</div>
                        <div class="trust-score-label">${label}</div>
                    </div>
                </div>
                
                ${components.length > 0 ? `
                    <div class="trust-components">
                        <h4>Score Components</h4>
                        ${components.map(comp => `
                            <div class="component-item">
                                <span class="component-label">${comp.label || comp.name}</span>
                                <div class="component-bar">
                                    <div class="component-fill" style="width: ${comp.value || comp.score}%; background: ${this.getComponentColor(comp.value || comp.score)};"></div>
                                </div>
                                <span class="component-value">${comp.value || comp.score}%</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
        
        return card;
    }

    createBiasCard(data) {
        if (!data || !data.bias_analysis) return null;
        
        const bias = data.bias_analysis;
        const overallBias = bias.overall_bias || bias.bias_level || 'Unknown';
        const politicalLean = bias.political_lean !== undefined ? 
            (bias.political_lean > 0.3 ? 'Right' : 
             bias.political_lean < -0.3 ? 'Left' : 'Center') : 'Unknown';
        const loadedPhrases = bias.loaded_phrases || [];
        const manipulationTactics = bias.manipulation_tactics || [];
        const biasDimensions = bias.bias_dimensions || {};
        const biasIndicators = bias.bias_indicators || [];
        
        const card = document.createElement('div');
        card.className = 'analysis-card bias-card';
        card.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">⚖️</span>
                <span>Bias Analysis</span>
            </div>
            
            <div class="bias-content">
                <div class="bias-summary">
                    <div class="bias-score">${overallBias}</div>
                    <div class="political-lean">Political Lean: <strong>${politicalLean}</strong></div>
                    ${bias.confidence ? `<div class="confidence">Confidence: ${bias.confidence}%</div>` : ''}
                </div>

                ${loadedPhrases.length > 0 ? `
                    <div class="loaded-phrases-section">
                        <h4>Loaded Language Found</h4>
                        <div class="loaded-phrases-list">
                            ${loadedPhrases.map(phrase => `
                                <div class="loaded-phrase-item">
                                    <div class="phrase-text">"${phrase.text || phrase.phrase || phrase}"</div>
                                    ${phrase.explanation ? `<div class="phrase-explanation">${phrase.explanation}</div>` : ''}
                                    ${phrase.context ? `<div class="phrase-context">Context: "${phrase.context}"</div>` : ''}
                                    ${phrase.impact ? `<div class="phrase-impact">Impact: <span class="impact-${phrase.impact}">${phrase.impact}</span></div>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                ${manipulationTactics.length > 0 ? `
                    <div class="manipulation-tactics-section">
                        <h4>Manipulation Tactics</h4>
                        <div class="tactics-list">
                            ${manipulationTactics.map(tactic => `
                                <div class="tactic-item">
                                    <div class="tactic-name">${tactic.name || tactic}</div>
                                    ${tactic.description ? `<div class="tactic-description">${tactic.description}</div>` : ''}
                                    ${tactic.severity ? `<div class="tactic-severity">Severity: <span class="severity-${tactic.severity}">${tactic.severity}</span></div>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                ${Object.keys(biasDimensions).length > 0 ? `
                    <div class="bias-dimensions-section">
                        <h4>Bias Dimensions</h4>
                        <div class="dimensions-grid">
                            ${Object.entries(biasDimensions).map(([key, dim]) => `
                                <div class="dimension-item">
                                    <div class="dimension-name">${key.charAt(0).toUpperCase() + key.slice(1)}</div>
                                    <div class="dimension-score">${dim.label || dim.score || dim}</div>
                                    ${dim.score !== undefined ? `
                                        <div class="dimension-bar">
                                            <div class="dimension-fill" style="width: ${Math.abs(dim.score) * 100}%"></div>
                                        </div>
                                    ` : ''}
                                    ${dim.confidence ? `<div class="dimension-confidence">Confidence: ${dim.confidence}%</div>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                ${biasIndicators.length > 0 ? `
                    <div class="bias-indicators-section">
                        <h4>Bias Indicators</h4>
                        <ul class="indicators-list">
                            ${biasIndicators.map(indicator => `<li>${indicator}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
        
        return card;
    }

    createFactsCard(data, isPro) {
        const card = document.createElement('div');
        card.className = 'analysis-card facts-card';
        
        // Always show full fact checks if we have them
        const factChecks = data.fact_checks || [];
        const keyClaims = data.key_claims || [];
        
        card.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">✓</span>
                <span>Fact Checking Results</span>
            </div>
            
            <div class="facts-content">
                <div class="facts-summary">
                    <div class="total-claims">${factChecks.length || keyClaims.length} claims analyzed</div>
                    ${this.getFactCheckSummary(factChecks)}
                </div>

                ${(factChecks.length > 0 || keyClaims.length > 0) ? `
                    <div class="fact-checks-list">
                        ${factChecks.length > 0 ? 
                            factChecks.map((check, index) => `
                                <div class="fact-check-item ${(check.verdict || check.rating || 'unknown').toLowerCase()}">
                                    <div class="fact-check-header">
                                        <span class="claim-number">#${index + 1}</span>
                                        <span class="verdict-badge">${check.verdict || check.rating || 'Not Verified'}</span>
                                    </div>
                                    <div class="claim-text">"${check.claim || check.text || 'Claim'}"</div>
                                    ${check.explanation ? `<div class="verdict-explanation">${check.explanation}</div>` : ''}
                                    ${check.evidence ? `
                                        <div class="evidence-section">
                                            <h5>Evidence:</h5>
                                            <div class="evidence-text">${check.evidence}</div>
                                        </div>
                                    ` : ''}
                                    ${check.source ? `
                                        <div class="source-info">
                                            <a href="${check.source}" target="_blank" rel="noopener">View Source →</a>
                                        </div>
                                    ` : ''}
                                </div>
                            `).join('') :
                            keyClaims.map((claim, index) => `
                                <div class="fact-check-item unverified">
                                    <div class="fact-check-header">
                                        <span class="claim-number">#${index + 1}</span>
                                        <span class="verdict-badge">Key Claim</span>
                                    </div>
                                    <div class="claim-text">"${claim.text || claim}"</div>
                                    <div class="verdict-explanation">This claim has not been independently verified.</div>
                                </div>
                            `).join('')
                        }
                    </div>
                ` : '<p>No fact checks available</p>'}
            </div>
        `;
        
        return card;
    }

    createAuthorCard(data) {
        const author = data.author_analysis || data.author_info || {};
        const article = data.article || {};
        const authorName = author.name || article.author || 'Unknown Author';
        const found = author.found !== undefined ? author.found : false;
        const credibilityScore = author.credibility_score || 0;
        const credentials = author.credentials || [];
        const expertise = author.expertise || [];
        const pastWork = author.past_work || [];
        
        const card = document.createElement('div');
        card.className = 'analysis-card author-card';
        card.setAttribute('data-card-type', 'author');
        
        card.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">✍️</span>
                <span>Author Analysis</span>
            </div>
            
            <div class="author-content">
                <div class="author-info">
                    <h3>${authorName}</h3>
                    
                    ${found ? `
                        <div class="author-found">
                            <div class="credibility-score">
                                <span class="score-label">Credibility Score:</span>
                                <span class="score-value" style="color: ${this.getCredibilityColor(credibilityScore)}">${credibilityScore}/100</span>
                            </div>
                            
                            ${author.position ? `
                                <div class="author-position">
                                    <strong>Position:</strong> ${author.position}
                                    ${author.organization ? ` at ${author.organization}` : ''}
                                </div>
                            ` : ''}
                            
                            ${author.bio ? `
                                <div class="author-bio">
                                    <strong>Bio:</strong> ${author.bio}
                                </div>
                            ` : ''}
                            
                            ${credentials.length > 0 ? `
                                <div class="credentials-section">
                                    <h4>Credentials</h4>
                                    <ul>
                                        ${credentials.map(cred => `<li>${cred}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                            
                            ${expertise.length > 0 ? `
                                <div class="expertise-section">
                                    <h4>Areas of Expertise</h4>
                                    <div class="expertise-tags">
                                        ${expertise.map(exp => `<span class="expertise-tag">${exp}</span>`).join('')}
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${pastWork.length > 0 ? `
                                <div class="past-work-section">
                                    <h4>Notable Past Work</h4>
                                    <ul>
                                        ${pastWork.map(work => `<li>${work}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}

                            ${author.social_media ? `
                                <div class="social-presence">
                                    <h4>Social Media Presence</h4>
                                    <p>${author.social_media}</p>
                                </div>
                            ` : ''}

                            ${author.verification_status ? `
                                <div class="verification-status">
                                    <span class="status-icon">✓</span>
                                    ${author.verification_status}
                                </div>
                            ` : ''}
                        </div>
                    ` : `
                        <div class="author-not-found">
                            <p class="warning-message">⚠️ Author information could not be verified</p>
                            <p>Unable to find credible information about this author. Consider researching the author independently.</p>
                        </div>
                    `}
                </div>
            </div>
        `;
        
        return card;
    }

    createClickbaitCard(data, isPro) {
        const clickbait = data.clickbait_analysis || {};
        const score = clickbait.score || data.clickbait_score || 0;
        const tactics = clickbait.tactics || [];
        const elements = clickbait.elements || [];
        
        const card = document.createElement('div');
        card.className = 'analysis-card clickbait-card';
        
        card.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">🎣</span>
                <span>Clickbait Detection</span>
            </div>
            
            <div class="clickbait-content">
                <div class="clickbait-score-display">
                    <div class="score-meter">
                        <div class="score-fill" style="width: ${score}%; background: ${this.getClickbaitColor(score)}"></div>
                    </div>
                    <div class="score-text">
                        <span class="score-number">${score}%</span>
                        <span class="score-label">${this.getClickbaitLabel(score)}</span>
                    </div>
                </div>
                
                ${tactics.length > 0 ? `
                    <div class="clickbait-tactics">
                        <h4>Clickbait Tactics Used</h4>
                        <ul>
                            ${tactics.map(tactic => `<li>${tactic}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${elements.length > 0 ? `
                    <div class="clickbait-elements">
                        <h4>Clickbait Elements Found</h4>
                        <div class="elements-list">
                            ${elements.map(element => `
                                <div class="element-item">
                                    <span class="element-type">${element.type}:</span>
                                    <span class="element-text">"${element.text}"</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        return card;
    }

    createSourceCard(data) {
        const source = data.source_credibility || {};
        const domain = data.article?.domain || 'Unknown';
        
        const card = document.createElement('div');
        card.className = 'analysis-card source-card';
        
        card.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">🏢</span>
                <span>Source Credibility</span>
            </div>
            
            <div class="source-content">
                <div class="source-domain">
                    <h3>${domain}</h3>
                </div>
                
                <div class="source-details">
                    ${source.credibility ? `
                        <div class="detail-item">
                            <span class="detail-label">Overall Credibility:</span>
                            <span class="detail-value credibility-${source.credibility.toLowerCase()}">${source.credibility}</span>
                        </div>
                    ` : ''}
                    
                    ${source.bias ? `
                        <div class="detail-item">
                            <span class="detail-label">Political Bias:</span>
                            <span class="detail-value bias-${source.bias.toLowerCase().replace(/\s+/g, '-')}">${source.bias}</span>
                        </div>
                    ` : ''}
                    
                    ${source.factual_reporting ? `
                        <div class="detail-item">
                            <span class="detail-label">Factual Reporting:</span>
                            <span class="detail-value">${source.factual_reporting}</span>
                        </div>
                    ` : ''}
                    
                    ${source.type ? `
                        <div class="detail-item">
                            <span class="detail-label">Source Type:</span>
                            <span class="detail-value">${source.type}</span>
                        </div>
                    ` : ''}
                    
                    ${source.traffic_rank ? `
                        <div class="detail-item">
                            <span class="detail-label">Traffic Rank:</span>
                            <span class="detail-value">#${source.traffic_rank}</span>
                        </div>
                    ` : ''}
                </div>
                
                ${source.description ? `
                    <div class="source-description">
                        <h4>About This Source</h4>
                        <p>${source.description}</p>
                    </div>
                ` : ''}
            </div>
        `;
        
        return card;
    }

    createManipulationCard(data) {
        const manipulation = data.manipulation_analysis || {};
        const score = manipulation.score || manipulation.manipulation_score || 0;
        const tactics = manipulation.tactics || [];
        const techniques = manipulation.techniques || [];
        
        const card = document.createElement('div');
        card.className = 'analysis-card manipulation-card';
        
        card.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">🎭</span>
                <span>Manipulation Detection</span>
            </div>
            
            <div class="manipulation-content">
                <div class="manipulation-score">
                    <div class="score-label">Manipulation Level</div>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${score}%; background: ${this.getManipulationColor(score)};"></div>
                    </div>
                    <div class="score-text">${score}% - ${this.getManipulationLabel(score)}</div>
                </div>
                
                ${tactics.length > 0 ? `
                    <div class="manipulation-tactics">
                        <h4>Manipulation Tactics Detected</h4>
                        <div class="tactics-list">
                            ${tactics.map(tactic => `
                                <div class="tactic-item">
                                    <span class="tactic-icon">⚠️</span>
                                    <div class="tactic-content">
                                        <div class="tactic-name">${tactic.name || tactic}</div>
                                        ${tactic.description ? `<div class="tactic-description">${tactic.description}</div>` : ''}
                                        ${tactic.examples && tactic.examples.length > 0 ? `
                                            <div class="tactic-examples">
                                                <strong>Examples:</strong>
                                                <ul>
                                                    ${tactic.examples.map(ex => `<li>"${ex}"</li>`).join('')}
                                                </ul>
                                            </div>
                                        ` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${techniques.length > 0 ? `
                    <div class="manipulation-techniques">
                        <h4>Persuasion Techniques</h4>
                        <ul>
                            ${techniques.map(tech => `<li>${tech}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
        
        return card;
    }

    createMetricsCard(data) {
        const metrics = data.article_metrics || data.content_analysis || {};
        const readability = data.readability_analysis || metrics.readability || {};
        const engagement = metrics.engagement || {};
        
        const card = document.createElement('div');
        card.className = 'analysis-card metrics-card';
        
        card.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">📊</span>
                <span>Article Metrics</span>
            </div>
            
            <div class="metrics-content">
                ${Object.keys(readability).length > 0 ? `
                    <div class="readability-section">
                        <h4>Readability Scores</h4>
                        <div class="metrics-grid">
                            ${Object.entries(readability).map(([key, value]) => `
                                <div class="metric-item">
                                    <span class="metric-label">${key.replace(/_/g, ' ')}:</span>
                                    <span class="metric-value">${value}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${data.article?.word_count || metrics.word_count ? `
                    <div class="metric-item">
                        <span class="metric-label">Word Count:</span>
                        <span class="metric-value">${data.article?.word_count || metrics.word_count}</span>
                    </div>
                ` : ''}
                
                ${metrics.sentence_count ? `
                    <div class="metric-item">
                        <span class="metric-label">Sentences:</span>
                        <span class="metric-value">${metrics.sentence_count}</span>
                    </div>
                ` : ''}
                
                ${metrics.paragraph_count ? `
                    <div class="metric-item">
                        <span class="metric-label">Paragraphs:</span>
                        <span class="metric-value">${metrics.paragraph_count}</span>
                    </div>
                ` : ''}
                
                ${data.article?.reading_time || engagement.estimated_read_time ? `
                    <div class="metric-item">
                        <span class="metric-label">Read Time:</span>
                        <span class="metric-value">${data.article?.reading_time || engagement.estimated_read_time}</span>
                    </div>
                ` : ''}
            </div>
        `;
        
        return card;
    }

    makeCollapsible(card) {
        const header = card.querySelector('.analysis-header');
        if (!header) return;
        
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            card.classList.toggle('collapsed');
        });
    }

    // Helper methods
    getFactCheckSummary(factChecks) {
        const counts = {};
        factChecks.forEach(check => {
            const verdict = check.verdict || check.rating || 'Unknown';
            counts[verdict] = (counts[verdict] || 0) + 1;
        });
        
        return `
            <div class="verdict-summary">
                ${Object.entries(counts).map(([verdict, count]) => `
                    <span class="verdict-count ${verdict.toLowerCase().replace(/\s+/g, '-')}">
                        ${count} ${verdict}
                    </span>
                `).join('')}
            </div>
        `;
    }

    getFactCheckIcon(verdict) {
        const icons = {
            'true': '✓',
            'mostly true': '✓',
            'half true': '◐',
            'mostly false': '✗',
            'false': '✗',
            'unverified': '?'
        };
        return icons[verdict?.toLowerCase()] || '?';
    }

    getComponentColor(value) {
        if (value >= 80) return '#10b981';
        if (value >= 60) return '#3b82f6';
        if (value >= 40) return '#f59e0b';
        return '#ef4444';
    }

    getCredibilityColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        return '#ef4444';
    }

    getClickbaitColor(score) {
        if (score >= 70) return '#ef4444';
        if (score >= 40) return '#f59e0b';
        return '#10b981';
    }

    getClickbaitLabel(score) {
        if (score >= 70) return 'High Clickbait';
        if (score >= 40) return 'Moderate Clickbait';
        return 'Low Clickbait';
    }

    getManipulationColor(score) {
        if (score >= 70) return '#ef4444';
        if (score >= 40) return '#f59e0b';
        return '#10b981';
    }

    getManipulationLabel(score) {
        if (score >= 70) return 'High Manipulation';
        if (score >= 40) return 'Moderate Manipulation';
        return 'Low Manipulation';
    }

    addExportSection(container, data) {
        const exportSection = document.createElement('div');
        exportSection.className = 'export-section';
        exportSection.innerHTML = `
            <div class="export-header">
                <h3>Export Analysis</h3>
                <p>Download your analysis report</p>
            </div>
            <div class="export-buttons">
                <button class="export-btn pdf-btn" onclick="exportAnalysis('pdf')">
                    <span class="export-icon">📄</span>
                    Export as PDF
                </button>
                <button class="export-btn json-btn" onclick="exportAnalysis('json')">
                    <span class="export-icon">💾</span>
                    Export as JSON
                </button>
            </div>
        `;
        
        container.appendChild(exportSection);
        
        // Store analysis data for export
        window.currentAnalysisData = data;
    }
}

// Export and register
window.AnalysisCards = AnalysisCards;

// Auto-register with UI controller if available
if (window.UI) {
    window.UI.registerComponent('analysisCards', new AnalysisCards());
    console.log('AnalysisCards: Registered with UI controller');
}

// Debug function
window.debugAnalysisCards = function() {
    console.log('=== ANALYSIS CARDS DEBUG ===');
    console.log('UI Controller exists:', !!window.UI);
    console.log('AnalysisCards registered:', !!(window.UI && window.UI.components && window.UI.components.analysisCards));
    
    // Check for author data in last analysis
    if (window.LAST_ANALYSIS_DATA) {
        console.log('Last analysis data:', window.LAST_ANALYSIS_DATA);
        console.log('Has author_analysis:', !!window.LAST_ANALYSIS_DATA.author_analysis);
        console.log('Has bias_analysis:', !!window.LAST_ANALYSIS_DATA.bias_analysis);
        console.log('Bias analysis details:', window.LAST_ANALYSIS_DATA.bias_analysis);
    }
};
