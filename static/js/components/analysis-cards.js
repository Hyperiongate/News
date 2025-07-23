// static/js/components/analysis-cards.js

class AnalysisCards {
    constructor() {
        this.expandedCards = new Set();
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'analysis-cards-container';
        
        // Only create cards that have data
        const cards = [
            this.createBiasCard(data),
            this.createFactCheckCard(data),
            this.createAuthorCard(data),
            this.createClickbaitCard(data),
            this.createTrustScoreCard(data)  // Add trust score card
        ].filter(card => card !== null);
        
        container.innerHTML = `
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
            <div class="analysis-card" data-card-type="bias" data-collapsed="true">
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
                            <span class="metric-label">Objectivity</span>
                            <span class="metric-value">${bias.objectivity_score || 0}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Opinion</span>
                            <span class="metric-value">${bias.opinion_percentage || 0}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Emotional</span>
                            <span class="metric-value">${bias.emotional_score || 0}%</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    createFactCheckCard(data) {
        if (!data.fact_checks || data.fact_checks.length === 0) return null;
        
        const verified = data.fact_checks.filter(fc => fc.verdict?.toLowerCase().includes('true')).length;
        const total = data.fact_checks.length;
        const percentage = Math.round((verified / total) * 100);
        
        return `
            <div class="analysis-card" data-card-type="factcheck" data-collapsed="true">
                <div class="card-header" onclick="window.analysisCards?.toggleCard('factcheck')">
                    <div class="card-title">
                        <span class="card-icon">✓</span>
                        <h4>Fact Check</h4>
                    </div>
                    <div class="card-preview">
                        <span class="preview-badge ${percentage >= 70 ? 'high' : percentage >= 40 ? 'medium' : 'low'}">${percentage}% verified</span>
                        <span class="card-toggle">▼</span>
                    </div>
                </div>
                <div class="card-content" style="display: none;">
                    <div class="metrics-grid">
                        <div class="metric">
                            <span class="metric-label">Verified</span>
                            <span class="metric-value">${verified}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Total Claims</span>
                            <span class="metric-value">${total}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Accuracy</span>
                            <span class="metric-value">${percentage}%</span>
                        </div>
                    </div>
                    ${this.renderCompactFactChecks(data.fact_checks.slice(0, 3))}
                </div>
            </div>
        `;
    }

    createAuthorCard(data) {
        if (!data.author_analysis || !data.author_analysis.name) return null;
        
        const author = data.author_analysis;
        const credScore = author.credibility_score || 'N/A';
        
        return `
            <div class="analysis-card" data-card-type="author" data-collapsed="true">
                <div class="card-header" onclick="window.analysisCards?.toggleCard('author')">
                    <div class="card-title">
                        <span class="card-icon">✍️</span>
                        <h4>Author</h4>
                    </div>
                    <div class="card-preview">
                        <span class="preview-badge ${credScore >= 70 ? 'high' : credScore >= 40 ? 'medium' : 'low'}">
                            ${typeof credScore === 'number' ? credScore + '% cred' : credScore}
                        </span>
                        <span class="card-toggle">▼</span>
                    </div>
                </div>
                <div class="card-content" style="display: none;">
                    <div class="author-details">
                        <h5>${author.name}</h5>
                        ${author.verified ? '<span class="verified-badge">✓ Verified</span>' : ''}
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric">
                            <span class="metric-label">Credibility</span>
                            <span class="metric-value">${credScore}${typeof credScore === 'number' ? '%' : ''}</span>
                        </div>
                        ${author.articles_count ? `
                            <div class="metric">
                                <span class="metric-label">Articles</span>
                                <span class="metric-value">${author.articles_count}</span>
                            </div>
                        ` : ''}
                        ${author.years_experience ? `
                            <div class="metric">
                                <span class="metric-label">Experience</span>
                                <span class="metric-value">${author.years_experience}y</span>
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
            <div class="analysis-card" data-card-type="clickbait" data-collapsed="true">
                <div class="card-header" onclick="window.analysisCards?.toggleCard('clickbait')">
                    <div class="card-title">
                        <span class="card-icon">🎣</span>
                        <h4>Clickbait</h4>
                    </div>
                    <div class="card-preview">
                        <span class="preview-badge ${level}">${score}% score</span>
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
                    
                    <div class="metrics-grid">
                        ${data.title_analysis ? `
                            <div class="metric">
                                <span class="metric-label">Sensational</span>
                                <span class="metric-value">${data.title_analysis.sensationalism}%</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Curiosity</span>
                                <span class="metric-value">${data.title_analysis.curiosity_gap}%</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Emotional</span>
                                <span class="metric-value">${data.title_analysis.emotional_words}%</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    createTrustScoreCard(data) {
        if (!data.analysis?.trust_score) return null;
        
        const score = data.analysis.trust_score;
        const level = score >= 80 ? 'excellent' : score >= 60 ? 'good' : score >= 40 ? 'fair' : 'poor';
        
        return `
            <div class="analysis-card" data-card-type="trust" data-collapsed="true">
                <div class="card-header" onclick="window.analysisCards?.toggleCard('trust')">
                    <div class="card-title">
                        <span class="card-icon">🛡️</span>
                        <h4>Trust Score</h4>
                    </div>
                    <div class="card-preview">
                        <span class="preview-badge ${level}">${score}/100</span>
                        <span class="card-toggle">▼</span>
                    </div>
                </div>
                <div class="card-content" style="display: none;">
                    <div class="trust-interpretation">
                        <p class="interpretation-text">
                            ${this.getTrustInterpretation(score)}
                        </p>
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric">
                            <span class="metric-label">Overall</span>
                            <span class="metric-value">${score}/100</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Rating</span>
                            <span class="metric-value">${level.charAt(0).toUpperCase() + level.slice(1)}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Reliability</span>
                            <span class="metric-value">${score >= 60 ? 'High' : 'Low'}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getTrustInterpretation(score) {
        if (score >= 80) return "This article demonstrates high credibility and can be considered a reliable source.";
        if (score >= 60) return "This article shows good credibility with minor concerns to be aware of.";
        if (score >= 40) return "This article has moderate credibility. Verify important claims independently.";
        return "This article shows low credibility. Seek additional sources for verification.";
    }

    renderCompactFactChecks(factChecks) {
        if (!factChecks || factChecks.length === 0) return '';
        
        return `
            <div class="fact-checks-compact">
                ${factChecks.map((fc, index) => `
                    <div class="fact-check-compact">
                        <div class="fc-header">
                            <span class="fc-verdict ${this.getVerdictClass(fc.verdict)}">
                                ${this.getVerdictIcon(fc.verdict)} ${this.formatVerdict(fc.verdict)}
                            </span>
                        </div>
                        <div class="fc-claim">"${fc.claim}"</div>
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
        const isCollapsed = card.getAttribute('data-collapsed') === 'true';
        
        if (isCollapsed) {
            content.style.display = 'block';
            toggle.textContent = '▲';
            card.setAttribute('data-collapsed', 'false');
            card.classList.add('expanded');
            this.expandedCards.add(cardType);
        } else {
            content.style.display = 'none';
            toggle.textContent = '▼';
            card.setAttribute('data-collapsed', 'true');
            card.classList.remove('expanded');
            this.expandedCards.delete(cardType);
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
