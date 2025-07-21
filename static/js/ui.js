/**
 * FILE: static/js/ui.js
 * LOCATION: news/static/js/ui.js
 * PURPOSE: Enhanced UI helper functions for News Analyzer
 */

const UI = {
    /**
     * Show resources used in analysis
     */
    showResources(data) {
        const resourcesDiv = document.getElementById('resources');
        const resourcesList = document.getElementById('resourcesList');
        
        const resources = [];
        
        // Add resources based on what was used
        if (data.analysis?.source_credibility) {
            resources.push('Source Credibility Database');
        }
        
        if (data.is_pro) {
            resources.push('OpenAI GPT-3.5');
            
            if (data.fact_checks?.length > 0) {
                resources.push('Google Fact Check API');
            }
            
            if (data.related_articles?.length > 0) {
                resources.push('News API');
            }
        } else {
            resources.push('Basic Analysis Engine');
        }
        
        // Clear and populate
        resourcesList.innerHTML = resources.map(r => 
            `<span class="resource-chip">${r}</span>`
        ).join('');
        
        resourcesDiv.classList.remove('hidden');
    },

    /**
     * Format and display trust score with visual meter
     */
    formatTrustScore(score) {
        const html = `
            <div class="trust-score-section">
                <h3>Overall Trust Score</h3>
                <div class="trust-meter">
                    <div class="trust-meter-bar">
                        <div id="trustMeterFill" class="trust-meter-fill ${this.getTrustClass(score)}" style="width: 0%"></div>
                    </div>
                </div>
                <div class="trust-score-value">${score}%</div>
                <div class="trust-score-label">Based on credibility, bias, and fact-checking</div>
            </div>
        `;
        
        // Animate the meter after rendering
        setTimeout(() => {
            const fill = document.getElementById('trustMeterFill');
            if (fill) {
                fill.style.width = `${score}%`;
            }
        }, 100);
        
        return html;
    },

    /**
     * Get trust score CSS class
     */
    getTrustClass(score) {
        if (score >= 70) return 'trust-high';
        if (score >= 40) return 'trust-medium';
        return 'trust-low';
    },

    /**
     * Create analysis cards grid
     */
    createAnalysisCards(data) {
        const cards = [];
        
        // Source Credibility Card
        if (data.source_credibility || data.article?.domain) {
            cards.push(this.createSourceCard(data));
        }
        
        // Bias Analysis Card
        cards.push(this.createBiasCard(data));
        
        // Manipulation Tactics Card
        if (data.manipulation_tactics?.length > 0) {
            cards.push(this.createManipulationCard(data));
        }
        
        // Fact Checks Card
        if (data.key_claims?.length > 0) {
            cards.push(this.createFactCheckCard(data));
        }
        
        return `<div class="analysis-grid">${cards.join('')}</div>`;
    },

    /**
     * Create source credibility card
     */
    createSourceCard(data) {
        const cred = data.source_credibility || {};
        const domain = data.article?.domain || 'Unknown';
        
        return `
            <div class="analysis-card">
                <div class="analysis-header">
                    <span class="analysis-icon">🏢</span>
                    <span>Source Credibility</span>
                </div>
                <div>
                    <p><strong>${domain}</strong></p>
                    <p>Credibility: <span style="color: ${this.getCredibilityColor(cred.credibility)}">${cred.credibility || 'Unknown'}</span></p>
                    <p>Bias: ${cred.bias || 'Unknown'}</p>
                    <p>Type: ${cred.type || 'Unknown'}</p>
                </div>
            </div>
        `;
    },

    /**
     * Create bias analysis card
     */
    createBiasCard(data) {
        const biasScore = data.bias_score || 0;
        const biasPercent = (biasScore + 1) * 50; // Convert -1 to 1 range to 0-100%
        
        let biasLabel = 'Center/Neutral';
        if (biasScore < -0.3) biasLabel = 'Left-leaning';
        else if (biasScore > 0.3) biasLabel = 'Right-leaning';
        
        return `
            <div class="analysis-card">
                <div class="analysis-header">
                    <span class="analysis-icon">📊</span>
                    <span>Bias Analysis</span>
                </div>
                <div>
                    <p>Political lean: <strong>${biasLabel}</strong></p>
                    <div class="bias-indicator">
                        <span style="color: #3b82f6;">Left</span>
                        <div class="bias-scale">
                            <div class="bias-marker" style="left: ${biasPercent}%"></div>
                        </div>
                        <span style="color: #ef4444;">Right</span>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Create manipulation tactics card
     */
    createManipulationCard(data) {
        const tactics = data.manipulation_tactics || [];
        
        return `
            <div class="analysis-card">
                <div class="analysis-header">
                    <span class="analysis-icon">⚠️</span>
                    <span>Manipulation Tactics</span>
                </div>
                <div>
                    ${tactics.length === 0 
                        ? '<p style="color: var(--gray);">No manipulation tactics detected</p>'
                        : `<ul class="manipulation-list">${tactics.map(t => `<li>${t}</li>`).join('')}</ul>`
                    }
                </div>
            </div>
        `;
    },

    /**
     * Create fact check card
     */
    createFactCheckCard(data) {
        const claims = data.key_claims || [];
        const factChecks = data.fact_checks || [];
        
        // Map fact checks to claims
        const claimsHtml = claims.map((claim, index) => {
            const check = factChecks[index];
            
            if (check) {
                const className = this.getFactCheckClass(check.verdict);
                const icon = this.getFactCheckIcon(check.verdict);
                
                return `
                    <div class="fact-check-item ${className}">
                        <span>${icon}</span>
                        <div>
                            <strong>${claim}</strong>
                            ${check.explanation ? `<br><small>${check.explanation}</small>` : ''}
                        </div>
                    </div>
                `;
            } else {
                return `
                    <div class="fact-check-item fact-unverified">
                        <span>?</span>
                        <div>${claim}</div>
                    </div>
                `;
            }
        }).join('');
        
        return `
            <div class="analysis-card">
                <div class="analysis-header">
                    <span class="analysis-icon">✓</span>
                    <span>Key Claims</span>
                </div>
                <div class="fact-check-list">
                    ${claimsHtml || '<p style="color: var(--gray);">No claims extracted</p>'}
                </div>
            </div>
        `;
    },

    /**
     * Create summary card
     */
    createSummaryCard(data) {
        const summary = data.summary || data.analysis?.summary || 'No summary available';
        
        return `
            <div class="analysis-card" style="margin-top: 1.5rem;">
                <div class="analysis-header">
                    <span class="analysis-icon">📝</span>
                    <span>Analysis Summary</span>
                </div>
                <div>
                    <p>${summary}</p>
                </div>
            </div>
        `;
    },

    /**
     * Get credibility color
     */
    getCredibilityColor(credibility) {
        switch(credibility?.toLowerCase()) {
            case 'high': return '#10b981';
            case 'medium': return '#f59e0b';
            case 'low': 
            case 'very low': return '#ef4444';
            default: return '#6b7280';
        }
    },

    /**
     * Get fact check class
     */
    getFactCheckClass(verdict) {
        switch(verdict?.toLowerCase()) {
            case 'true': return 'fact-true';
            case 'false': return 'fact-false';
            default: return 'fact-unverified';
        }
    },

    /**
     * Get fact check icon
     */
    getFactCheckIcon(verdict) {
        switch(verdict?.toLowerCase()) {
            case 'true': return '✓';
            case 'false': return '✗';
            case 'partially_true': return '≈';
            default: return '?';
        }
    },

    /**
     * Reset buttons functionality
     */
    setupResetButtons() {
        const resetBtn = document.getElementById('resetBtn');
        const resetTextBtn = document.getElementById('resetTextBtn');
        
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                document.getElementById('urlInput').value = '';
                document.getElementById('results').classList.add('hidden');
                document.getElementById('resources').classList.add('hidden');
            });
        }
        
        if (resetTextBtn) {
            resetTextBtn.addEventListener('click', () => {
                document.getElementById('textInput').value = '';
                document.getElementById('results').classList.add('hidden');
                document.getElementById('resources').classList.add('hidden');
            });
        }
    },

    /**
     * Show article info
     */
    createArticleInfo(article) {
        if (!article) return '';
        
        const items = [];
        
        if (article.title) {
            items.push(`<div class="result-item"><strong>Title:</strong> ${article.title}</div>`);
        }
        
        if (article.author) {
            items.push(`<div class="result-item"><strong>Author:</strong> ${article.author}</div>`);
        }
        
        if (article.domain) {
            items.push(`<div class="result-item"><strong>Source:</strong> ${article.domain}</div>`);
        }
        
        if (article.publish_date) {
            const date = new Date(article.publish_date).toLocaleDateString();
            items.push(`<div class="result-item"><strong>Published:</strong> ${date}</div>`);
        }
        
        return items.join('');
    }
};

// Initialize reset buttons when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    UI.setupResetButtons();
});
