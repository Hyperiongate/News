// static/js/components/analysis-cards.js

class AnalysisCards {
    constructor() {
        this.expandedCards = new Set();
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'analysis-cards-container';
        
        // Initially hide detailed view
        container.style.display = 'none';
        container.id = 'detailedAnalysisView';
        
        const cards = [
            this.createBiasCard(data),
            this.createFactCheckCard(data),
            this.createAuthorCard(data),
            this.createClickbaitCard(data),
            this.createSourceCard(data)
        ].filter(card => card !== null);
        
        container.innerHTML = `
            <div class="analysis-cards-header">
                <h3>Detailed Analysis</h3>
                <button class="expand-all-btn" onclick="window.analysisCards?.toggleAllCards()">
                    <span class="expand-icon">⊕</span>
                    <span class="expand-text">Expand All</span>
                </button>
            </div>
            <div class="analysis-cards-grid">
                ${cards.join('')}
            </div>
        `;
        
        // Add event listeners after rendering
        setTimeout(() => {
            this.attachEventListeners(container);
        }, 100);
        
        return container;
    }

    createBiasCard(data) {
        if (!data.bias_analysis) return null;
        
        const bias = data.bias_analysis;
        const biasLevel = Math.abs(bias.political_lean || 0);
        const biasDirection = bias.political_lean > 0 ? 'right' : bias.political_lean < 0 ? 'left' : 'center';
        
        return `
            <div class="analysis-card" data-card-type="bias">
                <div class="card-header" onclick="window.analysisCards?.toggleCard('bias')">
                    <div class="card-title">
                        <span class="card-icon">⚖️</span>
                        <h4>Bias Analysis</h4>
                    </div>
                    <div class="card-preview">
                        <span class="preview-badge ${biasDirection}">${bias.overall_bias || 'Unknown'}</span>
                        <span class="card-toggle">▼</span>
                    </div>
                </div>
                <div class="card-content" style="display: none;">
                    <div class="bias-meter">
                        <div class="meter-labels">
                            <span>Far Left</span>
                            <span>Center</span>
                            <span>Far Right</span>
                        </div>
                        <div class="meter-track">
                            <div class="meter-indicator" style="left: ${50 + (bias.political_lean || 0) / 2}%"></div>
                        </div>
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric">
                            <span class="metric-label">Objectivity Score</span>
                            <span class="metric-value">${bias.objectivity_score || 0}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Opinion Content</span>
                            <span class="metric-value">${bias.opinion_percentage || 0}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Emotional Language</span>
                            <span class="metric-value">${bias.emotional_score || 0}%</span>
                        </div>
                    </div>
                    
                    ${bias.manipulation_tactics?.length > 0 ? `
                        <div class="subsection">
                            <h5>Detected Manipulation Tactics:</h5>
                            <div class="tactics-list">
                                ${bias.manipulation_tactics.map(tactic => `
                                    <div class="tactic-item">
                                        <span class="tactic-icon">⚠️</span>
                                        <span class="tactic-name">${tactic.name || tactic}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${bias.loaded_phrases?.length > 0 ? `
                        <div class="subsection">
                            <h5>Loaded Language Examples:</h5>
                            <div class="phrases-list">
                                ${bias.loaded_phrases.slice(0, 3).map(phrase => `
                                    <div class="phrase-item">
                                        <span class="phrase-type">${phrase.type}</span>
                                        <span class="phrase-text">"${phrase.text}"</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    createFactCheckCard(data) {
        if (!data.fact_checks || data.fact_checks.length === 0) return null;
        
        const verified = data.fact_checks.filter(fc => fc.verdict?.toLowerCase().includes('true')).length;
        const total = data.fact_checks.length;
        
        return `
            <div class="analysis-card" data-card-type="factcheck">
                <div class="card-header" onclick="window.analysisCards?.toggleCard('factcheck')">
                    <div class="card-title">
                        <span class="card-icon">✓</span>
                        <h4>Fact Check Results</h4>
                    </div>
                    <div class="card-preview">
                        <span class="preview-text">${verified}/${total} verified</span>
                        <span class="card-toggle">▼</span>
                    </div>
                </div>
                <div class="card-content" style="display: none;">
                    ${this.renderCompactFactChecks(data.fact_checks)}
                </div>
            </div>
        `;
    }

    createAuthorCard(data) {
        if (!data.author_analysis || !data.author_analysis.name) return null;
        
        const author = data.author_analysis;
        
        return `
            <div class="analysis-card" data-card-type="author">
                <div class="card-header" onclick="window.analysisCards?.toggleCard('author')">
                    <div class="card-title">
                        <span class="card-icon">✍️</span>
                        <h4>Author Analysis</h4>
                    </div>
                    <div class="card-preview">
                        <span class="preview-text">${author.name}</span>
                        <span class="card-toggle">▼</span>
                    </div>
                </div>
                <div class="card-content" style="display: none;">
                    <div class="author-details">
                        <div class="author-header">
                            <h5>${author.name}</h5>
                            ${author.verified ? '<span class="verified-badge">✓ Verified</span>' : ''}
                        </div>
                        
                        <div class="author-metrics">
                            <div class="metric">
                                <span class="metric-label">Credibility Score</span>
                                <span class="metric-value">${author.credibility_score || 'N/A'}</span>
                            </div>
                            ${author.articles_count ? `
                                <div class="metric">
                                    <span class="metric-label">Articles Written</span>
                                    <span class="metric-value">${author.articles_count}</span>
                                </div>
                            ` : ''}
                            ${author.years_experience ? `
                                <div class="metric">
                                    <span class="metric-label">Years Experience</span>
                                    <span class="metric-value">${author.years_experience}</span>
                                </div>
                            ` : ''}
                        </div>
                        
                        ${author.bio ? `
                            <div class="author-bio">
                                <p>${author.bio}</p>
                            </div>
                        ` : ''}
                        
                        ${author.expertise?.length > 0 ? `
                            <div class="author-expertise">
                                <h6>Areas of Expertise:</h6>
                                <div class="expertise-tags">
                                    ${author.expertise.map(area => 
                                        `<span class="expertise-tag">${area}</span>`
                                    ).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    createClickbaitCard(data) {
        if (data.clickbait_score === undefined) return null;
        
        const score = data.clickbait_score;
        const level = score > 70 ? 'high' : score > 40 ? 'medium' : 'low';
        
        return `
            <div class="analysis-card" data-card-type="clickbait">
                <div class="card-header" onclick="window.analysisCards?.toggleCard('clickbait')">
                    <div class="card-title">
                        <span class="card-icon">🎣</span>
                        <h4>Clickbait Detection</h4>
                    </div>
                    <div class="card-preview">
                        <span class="preview-badge ${level}">${score}% clickbait</span>
                        <span class="card-toggle">▼</span>
                    </div>
                </div>
                <div class="card-content" style="display: none;">
                    <div class="clickbait-gauge">
                        <div class="gauge-fill" style="width: ${score}%"></div>
                        <div class="gauge-labels">
                            <span>Genuine</span>
                            <span>Clickbait</span>
                        </div>
                    </div>
                    
                    ${data.clickbait_indicators?.length > 0 ? `
                        <div class="indicators-list">
                            <h5>Detected Indicators:</h5>
                            ${data.clickbait_indicators.map(indicator => `
                                <div class="indicator-item">
                                    <span class="indicator-icon">📌</span>
                                    <div class="indicator-content">
                                        <strong>${indicator.name}</strong>
                                        <p>${indicator.description}</p>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    ${data.title_analysis ? `
                        <div class="title-metrics">
                            <h5>Title Analysis:</h5>
                            <div class="metrics-grid">
                                <div class="metric">
                                    <span class="metric-label">Sensationalism</span>
                                    <span class="metric-value">${data.title_analysis.sensationalism}%</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Curiosity Gap</span>
                                    <span class="metric-value">${data.title_analysis.curiosity_gap}%</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Emotional Words</span>
                                    <span class="metric-value">${data.title_analysis.emotional_words}%</span>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    createSourceCard(data) {
        if (!data.analysis?.source_credibility) return null;
        
        const source = data.analysis.source_credibility;
        
        return `
            <div class="analysis-card" data-card-type="source">
                <div class="card-header" onclick="window.analysisCards?.toggleCard('source')">
                    <div class="card-title">
                        <span class="card-icon">🏢</span>
                        <h4>Source Credibility</h4>
                    </div>
                    <div class="card-preview">
                        <span class="preview-badge ${source.rating?.toLowerCase()}">${source.rating}</span>
                        <span class="card-toggle">▼</span>
                    </div>
                </div>
                <div class="card-content" style="display: none;">
                    <div class="source-details">
                        <h5>${data.article?.domain || 'Unknown Source'}</h5>
                        
                        <div class="source-metrics">
                            <div class="metric">
                                <span class="metric-label">Credibility</span>
                                <span class="metric-value">${source.rating}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Political Bias</span>
                                <span class="metric-value">${source.bias || 'Unknown'}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Type</span>
                                <span class="metric-value">${source.type || 'Unknown'}</span>
                            </div>
                        </div>
                        
                        ${source.description ? `
                            <div class="source-description">
                                <p>${source.description}</p>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    renderCompactFactChecks(factChecks) {
        return `
            <div class="fact-checks-compact">
                ${factChecks.slice(0, 5).map((fc, index) => `
                    <div class="fact-check-compact">
                        <div class="fc-header">
                            <span class="fc-verdict ${this.getVerdictClass(fc.verdict)}">
                                ${this.getVerdictIcon(fc.verdict)} ${this.formatVerdict(fc.verdict)}
                            </span>
                        </div>
                        <div class="fc-claim">"${fc.claim}"</div>
                        ${fc.explanation ? `<div class="fc-explanation">${fc.explanation}</div>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }

    getVerdictClass(verdict) {
        if (!verdict) return 'unverified';
        const v = verdict.toLowerCase();
        if (v.includes('true')) return 'true';
        if (v.includes('false')) return 'false';
        if (v.includes('mixed') || v.includes('partial')) return 'mixed';
        return 'unverified';
    }

    getVerdictIcon(verdict) {
        const verdictClass = this.getVerdictClass(verdict);
        const icons = {
            'true': '✓',
            'false': '✗',
            'mixed': '≈',
            'unverified': '?'
        };
        return icons[verdictClass] || '?';
    }

    formatVerdict(verdict) {
        if (!verdict) return 'Unverified';
        return verdict.charAt(0).toUpperCase() + verdict.slice(1).toLowerCase();
    }

    toggleCard(cardType) {
        const card = document.querySelector(`[data-card-type="${cardType}"]`);
        if (!card) return;
        
        const content = card.querySelector('.card-content');
        const toggle = card.querySelector('.card-toggle');
        
        if (content.style.display === 'none') {
            content.style.display = 'block';
            toggle.textContent = '▲';
            this.expandedCards.add(cardType);
        } else {
            content.style.display = 'none';
            toggle.textContent = '▼';
            this.expandedCards.delete(cardType);
        }
    }

    toggleAllCards() {
        const allCards = document.querySelectorAll('.analysis-card');
        const shouldExpand = this.expandedCards.size < allCards.length;
        
        allCards.forEach(card => {
            const cardType = card.getAttribute('data-card-type');
            const content = card.querySelector('.card-content');
            const toggle = card.querySelector('.card-toggle');
            
            if (shouldExpand) {
                content.style.display = 'block';
                toggle.textContent = '▲';
                this.expandedCards.add(cardType);
            } else {
                content.style.display = 'none';
                toggle.textContent = '▼';
                this.expandedCards.delete(cardType);
            }
        });
        
        // Update button text
        const btn = document.querySelector('.expand-all-btn');
        if (btn) {
            btn.querySelector('.expand-icon').textContent = shouldExpand ? '⊖' : '⊕';
            btn.querySelector('.expand-text').textContent = shouldExpand ? 'Collapse All' : 'Expand All';
        }
    }

    attachEventListeners(container) {
        // Event listeners are attached via onclick in the HTML
    }
}

// Create global instance
window.analysisCards = new AnalysisCards();

// Register with UI
document.addEventListener('DOMContentLoaded', () => {
    if (window.UI) {
        window.UI.registerComponent('analysisCards', window.analysisCards);
    }
});
