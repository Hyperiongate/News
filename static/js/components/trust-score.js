// static/js/components/trust-score.js

class TrustScore {
    constructor() {
        this.score = 0;
    }

    render(score, data) {
        this.score = score || 0;
        
        const container = document.createElement('div');
        container.className = 'trust-score-container';
        
        // Determine score category
        const category = this.getScoreCategory(this.score);
        
        container.innerHTML = `
            <div class="trust-score-card ${category.class}">
                <div class="trust-score-header">
                    <h3>Overall Trust Score</h3>
                    <span class="trust-badge">${category.label}</span>
                </div>
                
                <div class="trust-score-visual">
                    <div class="score-circle">
                        <svg viewBox="0 0 200 200" class="score-svg">
                            <circle cx="100" cy="100" r="90" fill="none" stroke="#e5e7eb" stroke-width="12"/>
                            <circle cx="100" cy="100" r="90" fill="none" 
                                stroke="${category.color}" 
                                stroke-width="12"
                                stroke-linecap="round"
                                stroke-dasharray="${this.getCircumference()}"
                                stroke-dashoffset="${this.getOffset()}"
                                transform="rotate(-90 100 100)"
                                class="score-progress"/>
                        </svg>
                        <div class="score-text">
                            <span class="score-number">${this.score}</span>
                            <span class="score-label">out of 100</span>
                        </div>
                    </div>
                    
                    <div class="score-details">
                        ${this.renderScoreFactors(data)}
                    </div>
                </div>
                
                <div class="trust-interpretation">
                    <p class="interpretation-text">${category.interpretation}</p>
                    ${this.renderRecommendation(category)}
                </div>
                
                <div class="trust-factors-summary">
                    ${this.renderFactorsSummary(data)}
                </div>
            </div>
        `;
        
        // Animate the score circle after rendering
        setTimeout(() => {
            const circle = container.querySelector('.score-progress');
            if (circle) {
                circle.style.transition = 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
                circle.style.strokeDashoffset = this.getOffset();
            }
        }, 100);
        
        return container;
    }

    getCircumference() {
        return 2 * Math.PI * 90;
    }

    getOffset() {
        const circumference = this.getCircumference();
        return circumference - (this.score / 100) * circumference;
    }

    getScoreCategory(score) {
        if (score >= 80) {
            return {
                class: 'excellent',
                label: 'Highly Trustworthy',
                color: '#10b981',
                interpretation: 'This article demonstrates exceptional credibility with minimal bias and strong factual accuracy.',
                recommendation: 'This source can be confidently used for research and citation.'
            };
        } else if (score >= 60) {
            return {
                class: 'good',
                label: 'Generally Reliable',
                color: '#3b82f6',
                interpretation: 'This article is reasonably trustworthy with some minor concerns that don\'t significantly impact credibility.',
                recommendation: 'Good for general information, but verify critical claims independently.'
            };
        } else if (score >= 40) {
            return {
                class: 'fair',
                label: 'Mixed Reliability',
                color: '#f59e0b',
                interpretation: 'This article shows notable bias or credibility issues that require careful consideration.',
                recommendation: 'Use with caution and cross-reference important information with other sources.'
            };
        } else {
            return {
                class: 'poor',
                label: 'Low Credibility',
                color: '#ef4444',
                interpretation: 'Significant concerns detected including potential misinformation, heavy bias, or manipulation tactics.',
                recommendation: 'Not recommended as a reliable source. Seek alternative sources for this information.'
            };
        }
    }

    renderScoreFactors(data) {
        const factors = this.extractFactors(data);
        
        return factors.map(factor => `
            <div class="score-factor">
                <span class="factor-icon">${factor.icon}</span>
                <span class="factor-label">${factor.label}</span>
                <span class="factor-value ${factor.class}">${factor.value}</span>
            </div>
        `).join('');
    }

    extractFactors(data) {
        const factors = [];
        
        // Source credibility
        if (data?.analysis?.source_credibility?.rating) {
            factors.push({
                icon: '🏢',
                label: 'Source',
                value: data.analysis.source_credibility.rating,
                class: this.getRatingClass(data.analysis.source_credibility.rating)
            });
        }
        
        // Author credibility
        if (data?.author_analysis?.credibility_score !== undefined) {
            const score = data.author_analysis.credibility_score;
            factors.push({
                icon: '✍️',
                label: 'Author',
                value: score >= 70 ? 'Verified' : score >= 40 ? 'Known' : 'Unknown',
                class: score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low'
            });
        }
        
        // Bias level
        if (data?.bias_analysis?.objectivity_score !== undefined) {
            const objectivity = data.bias_analysis.objectivity_score;
            factors.push({
                icon: '⚖️',
                label: 'Objectivity',
                value: `${objectivity}%`,
                class: objectivity >= 70 ? 'high' : objectivity >= 40 ? 'medium' : 'low'
            });
        }
        
        // Fact check results
        if (data?.fact_checks && data.fact_checks.length > 0) {
            const verified = data.fact_checks.filter(fc => 
                fc.verdict && fc.verdict.toLowerCase().includes('true')
            ).length;
            const percentage = Math.round((verified / data.fact_checks.length) * 100);
            factors.push({
                icon: '✓',
                label: 'Facts',
                value: `${percentage}%`,
                class: percentage >= 80 ? 'high' : percentage >= 50 ? 'medium' : 'low'
            });
        }
        
        return factors;
    }

    getRatingClass(rating) {
        const r = rating.toLowerCase();
        if (r === 'high') return 'high';
        if (r === 'medium') return 'medium';
        return 'low';
    }

    renderRecommendation(category) {
        return `
            <div class="recommendation">
                <span class="recommendation-icon">💡</span>
                <span class="recommendation-text">${category.recommendation}</span>
            </div>
        `;
    }

    renderFactorsSummary(data) {
        const summaryPoints = [];
        
        // Source analysis
        if (data?.analysis?.source_credibility) {
            const source = data.analysis.source_credibility;
            summaryPoints.push(`Source (${data.article?.domain || 'Unknown'}) has ${source.rating || 'unknown'} credibility`);
        }
        
        // Bias detection
        if (data?.bias_analysis?.manipulation_tactics?.length > 0) {
            summaryPoints.push(`${data.bias_analysis.manipulation_tactics.length} manipulation tactics detected`);
        }
        
        // Clickbait
        if (data?.clickbait_score > 50) {
            summaryPoints.push('High clickbait indicators in headline');
        }
        
        if (summaryPoints.length === 0) return '';
        
        return `
            <div class="factors-summary">
                <h4>Key Factors:</h4>
                <ul>
                    ${summaryPoints.map(point => `<li>${point}</li>`).join('')}
                </ul>
            </div>
        `;
    }
}

// Create and register
window.TrustScore = TrustScore;

document.addEventListener('DOMContentLoaded', () => {
    if (window.UI) {
        window.UI.registerComponent('trustScore', new TrustScore());
    }
});
