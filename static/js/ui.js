/**
 * FILE: static/js/ui.js
 * LOCATION: news/static/js/ui.js
 * PURPOSE: Enhanced UI with author credibility display
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
        
        if (data.author_analysis) {
            resources.push('Author Background Check');
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
                <div class="trust-score-label">Based on source credibility, author background, bias analysis, and fact-checking</div>
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
     * Create article summary section
     */
    createArticleSummary(data) {
        if (!data.article_summary && !data.conversational_summary) {
            return '';
        }
        
        return `
            <div class="analysis-card" style="margin-bottom: 1.5rem;">
                <div class="analysis-header">
                    <span class="analysis-icon">📋</span>
                    <span>Article Summary</span>
                </div>
                <div>
                    ${data.article_summary ? `<p style="margin-bottom: 1rem;">${data.article_summary}</p>` : ''}
                    ${data.conversational_summary ? `
                        <div style="background: #f3f4f6; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                            <strong>Our Analysis:</strong><br>
                            ${data.conversational_summary}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    },

    /**
     * Create author analysis card
     */
    createAuthorCard(data) {
        const author = data.author_analysis;
        const articleAuthor = data.article?.author;
        
        if (!author && !articleAuthor) {
            return '';
        }
        
        let html = `
            <div class="analysis-card" style="grid-column: 1 / -1;">
                <div class="analysis-header">
                    <span class="analysis-icon">✍️</span>
                    <span>Author Credibility</span>
                </div>
                <div>
        `;
        
        if (author && author.found) {
            // Author name and basic info
            html += `<h4 style="margin-bottom: 0.5rem;">${author.name}</h4>`;
            
            // Credibility assessment
            if (author.credibility_assessment) {
                html += `<p style="margin-bottom: 1rem;">${author.credibility_assessment}</p>`;
            }
            
            // Author website/profile
            if (author.website) {
                html += `<p><strong>Profile:</strong> <a href="${author.website}" target="_blank" style="color: var(--primary);">View author's profile →</a></p>`;
            }
            
            // Previous work
            if (author.previous_work && author.previous_work.length > 0) {
                html += `
                    <div style="margin-top: 1rem;">
                        <strong>Recent Articles by ${author.name}:</strong>
                        <ul style="margin-top: 0.5rem; margin-left: 1.5rem;">
                `;
                
                author.previous_work.slice(0, 3).forEach(article => {
                    html += `
                        <li style="margin-bottom: 0.5rem;">
                            <a href="${article.url}" target="_blank" style="color: var(--primary);">
                                ${article.title}
                            </a>
                            ${article.source ? ` <span style="color: var(--gray); font-size: 0.9rem;">(${article.source})</span>` : ''}
                        </li>
                    `;
                });
                
                html += `</ul></div>`;
            }
            
            // Awards/recognition
            if (author.awards && author.awards.length > 0) {
                html += `
                    <div style="margin-top: 1rem; padding: 0.75rem; background: #fef3c7; border-radius: 6px;">
                        <strong>🏆 Recognition:</strong> ${author.awards[0]}
                    </div>
                `;
            }
            
            // Credibility score visualization
            if (author.credibility_score !== null) {
                const scoreClass = author.credibility_score >= 70 ? 'trust-high' : 
                                 author.credibility_score >= 40 ? 'trust-medium' : 'trust-low';
                html += `
                    <div style="margin-top: 1rem;">
                        <strong>Author Credibility Score:</strong>
                        <div style="display: flex; align-items: center; gap: 1rem; margin-top: 0.5rem;">
                            <div style="flex: 1; height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden;">
                                <div class="${scoreClass}" style="height: 100%; width: ${author.credibility_score}%; transition: width 1s ease-out;"></div>
                            </div>
                            <span style="font-weight: 600;">${author.credibility_score}%</span>
                        </div>
                    </div>
                `;
            }
        } else {
            // No author analysis available
            html += `
                <p><strong>Author:</strong> ${articleAuthor || 'Not specified'}</p>
                <p style="color: var(--gray); margin-top: 0.5rem;">
                    Author background information not available. Consider researching the author independently to verify credentials.
                </p>
            `;
        }
        
        html += `</div></div>`;
        
        return html;
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
     * Show article info with proper citation
     */
    createArticleInfo(article) {
        if (!article) return '';
        
        let html = '<div style="background: #f9fafb; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">';
        
        // Proper citation format
        if (article.author && article.domain && article.title) {
            html += `<p style="font-size: 1.1rem; margin-bottom: 0.5rem;">
                <strong>${article.title}</strong>
            </p>`;
            html += `<p style="color: var(--gray);">
                By ${article.author} | ${article.domain}
                ${article.publish_date ? ` | ${new Date(article.publish_date).toLocaleDateString()}` : ''}
            </p>`;
        } else {
            if (article.title) {
                html += `<p><strong>Title:</strong> ${article.title}</p>`;
            }
            if (article.author) {
                html += `<p><strong>Author:</strong> ${article.author}</p>`;
            }
            if (article.domain) {
                html += `<p><strong>Source:</strong> ${article.domain}</p>`;
            }
        }
        
        html += '</div>';
        
        return html;
    }
};

// Initialize reset buttons when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    UI.setupResetButtons();
});
