// static/js/components/executive-summary.js

class ExecutiveSummary {
    constructor() {
        this.data = null; 
    }

    render(data) {
        this.data = data;
        
        const container = document.createElement('div');
        container.className = 'executive-summary-container';
        
        // Generate insights
        const insights = this.generateInsights(data);
        
        container.innerHTML = `
            <div class="executive-summary-card">
                <div class="summary-header">
                    <div class="header-content">
                        <h2>Executive Summary</h2>
                        <p class="summary-subtitle">AI-powered analysis of article credibility and content</p>
                    </div>
                    <div class="summary-timestamp">
                        <span class="timestamp-icon">🕐</span>
                        <span>${new Date().toLocaleTimeString()}</span>
                    </div>
                </div>
                
                <div class="summary-sections">
                    ${this.renderWhatWeAnalyzed(data)}
                    ${this.renderWhatWeFound(insights)}
                    ${this.renderWhatItMeans(insights)}
                    ${this.renderQuickActions(data)}
                </div>
            </div>
        `;
        
        return container;
    }

    generateInsights(data) {
        const insights = {
            mainFindings: [],
            concerns: [],
            strengths: [],
            verdict: '',
            actionableAdvice: ''
        };
        
        // Trust score insight
        const trustScore = data.trust_score || 0;
        if (trustScore >= 80) {
            insights.verdict = 'This article appears to be a reliable source of information.';
            insights.strengths.push('High overall credibility score');
        } else if (trustScore >= 60) {
            insights.verdict = 'This article is generally trustworthy with some areas of concern.';
        } else if (trustScore >= 40) {
            insights.verdict = 'This article requires careful verification of key claims.';
        } else {
            insights.verdict = 'This article shows significant credibility issues.';
            insights.concerns.push('Low overall trust score indicates reliability problems');
        }
        
        // Source credibility
        if (data.analysis?.source_credibility?.rating) {
            const rating = data.analysis.source_credibility.rating;
            if (rating === 'High') {
                insights.strengths.push(`Published by ${data.article?.domain}, a highly credible source`);
            } else if (rating === 'Low' || rating === 'Very Low') {
                insights.concerns.push(`Source (${data.article?.domain}) has known credibility issues`);
            }
        }
        
        // Author analysis
        if (data.author_analysis?.credibility_score) {
            const authorScore = data.author_analysis.credibility_score;
            const authorName = data.author_analysis.name || 'The author';
            if (authorScore >= 70) {
                insights.strengths.push(`${authorName} is a verified journalist with established credentials`);
            } else if (authorScore < 40) {
                insights.concerns.push(`Limited information available about the author's background`);
            }
        }
        
        // Bias analysis
        if (data.bias_analysis) {
            const bias = data.bias_analysis;
            if (Math.abs(bias.political_lean) > 60) {
                insights.concerns.push(`Strong ${bias.political_lean > 0 ? 'right' : 'left'}-leaning bias detected`);
            }
            if (bias.manipulation_tactics?.length > 2) {
                insights.concerns.push(`${bias.manipulation_tactics.length} manipulation tactics identified`);
            }
            if (bias.objectivity_score > 80) {
                insights.strengths.push('High objectivity score indicates balanced reporting');
            }
        }
        
        // Fact checking
        if (data.fact_checks && data.fact_checks.length > 0) {
            const verified = data.fact_checks.filter(fc => 
                fc.verdict && fc.verdict.toLowerCase().includes('true')
            ).length;
            const false_claims = data.fact_checks.filter(fc => 
                fc.verdict && fc.verdict.toLowerCase().includes('false')
            ).length;
            
            if (false_claims > 0) {
                insights.concerns.push(`${false_claims} false claim${false_claims > 1 ? 's' : ''} detected`);
            }
            if (verified === data.fact_checks.length) {
                insights.strengths.push('All checked claims verified as accurate');
            }
        }
        
        // Clickbait
        if (data.clickbait_score > 60) {
            insights.concerns.push('Headline uses clickbait techniques');
        }
        
        // Generate actionable advice
        if (insights.concerns.length === 0) {
            insights.actionableAdvice = 'This article can be confidently used as a reference source.';
        } else if (insights.concerns.length <= 2) {
            insights.actionableAdvice = 'Proceed with standard verification of key facts before citing.';
        } else {
            insights.actionableAdvice = 'We recommend finding additional sources to verify this information.';
        }
        
        return insights;
    }

    renderWhatWeAnalyzed(data) {
        const items = [];
        
        if (data.article?.domain) {
            items.push(`Article from ${data.article.domain}`);
        }
        if (data.author_analysis?.name) {
            items.push(`Written by ${data.author_analysis.name}`);
        }
        if (data.article?.publish_date) {
            const date = new Date(data.article.publish_date);
            items.push(`Published ${date.toLocaleDateString()}`);
        }
        if (data.key_claims?.length) {
            items.push(`${data.key_claims.length} factual claims identified`);
        }
        
        return `
            <div class="summary-section">
                <h3>
                    <span class="section-icon">🔍</span>
                    What We Analyzed
                </h3>
                <div class="section-content">
                    <p>${items.join(' • ')}</p>
                    ${data.article?.title ? `<blockquote>"${data.article.title}"</blockquote>` : ''}
                </div>
            </div>
        `;
    }

    renderWhatWeFound(insights) {
        const allFindings = [
            ...insights.strengths.map(s => ({ text: s, type: 'strength' })),
            ...insights.concerns.map(c => ({ text: c, type: 'concern' }))
        ];
        
        if (allFindings.length === 0) {
            allFindings.push({ text: 'Standard news article with typical characteristics', type: 'neutral' });
        }
        
        return `
            <div class="summary-section">
                <h3>
                    <span class="section-icon">📊</span>
                    What We Found
                </h3>
                <div class="section-content">
                    <div class="findings-list">
                        ${allFindings.map(finding => `
                            <div class="finding-item ${finding.type}">
                                <span class="finding-icon">${finding.type === 'strength' ? '✅' : finding.type === 'concern' ? '⚠️' : 'ℹ️'}</span>
                                <span class="finding-text">${finding.text}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    renderWhatItMeans(insights) {
        return `
            <div class="summary-section">
                <h3>
                    <span class="section-icon">💡</span>
                    What It Means
                </h3>
                <div class="section-content">
                    <p class="verdict">${insights.verdict}</p>
                    <div class="advice-box">
                        <strong>Our Recommendation:</strong> ${insights.actionableAdvice}
                    </div>
                </div>
            </div>
        `;
    }

    renderQuickActions(data) {
        return `
            <div class="quick-actions">
                <button class="action-btn primary" onclick="window.exportHandler?.exportPDF()">
                    <span class="action-icon">📄</span>
                    Export Report as PDF
                </button>
                <button class="action-btn secondary" onclick="window.UI?.toggleDetailedView()">
                    <span class="action-icon">📊</span>
                    View Detailed Analysis
                </button>
                ${data.article?.url ? `
                    <a href="${data.article.url}" target="_blank" class="action-btn secondary">
                        <span class="action-icon">🔗</span>
                        View Original Article
                    </a>
                ` : ''}
            </div>
        `;
    }
}

// Create and register
window.ExecutiveSummary = ExecutiveSummary;

document.addEventListener('DOMContentLoaded', () => {
    if (window.UI) {
        window.UI.registerComponent('executiveSummary', new ExecutiveSummary());
    }
});
