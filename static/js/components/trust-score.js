// static/js/components/trust-score.js

class TrustScore {
    constructor() {
        this.score = 0;
        this.container = null;
    }

    render(score) {
        this.score = score || 0;
        
        const container = document.createElement('div');
        container.className = 'trust-score-container analysis-card';
        container.style.cssText = 'margin-bottom: 1.5rem;';
        
        // Determine color and status based on score
        const { color, status, description } = this.getScoreDetails(this.score);
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">🛡️</span>
                <span>Overall Trust Score</span>
            </div>
            
            <div class="trust-score-content">
                <div class="trust-score-main">
                    <div class="trust-score-visual">
                        <svg class="trust-score-meter" width="200" height="120" viewBox="0 0 200 120">
                            <!-- Background arc -->
                            <path 
                                d="M 20 100 A 80 80 0 0 1 180 100" 
                                fill="none" 
                                stroke="#e5e7eb" 
                                stroke-width="20"
                                stroke-linecap="round"
                            />
                            
                            <!-- Score arc -->
                            <path 
                                d="M 20 100 A 80 80 0 0 1 180 100" 
                                fill="none" 
                                stroke="${color}" 
                                stroke-width="20"
                                stroke-linecap="round"
                                stroke-dasharray="${this.calculateArcLength(this.score)} 251.33"
                                class="trust-score-arc"
                                style="transition: stroke-dasharray 1s ease-in-out;"
                            />
                            
                            <!-- Score sections -->
                            <text x="30" y="115" font-size="10" fill="#9ca3af">0</text>
                            <text x="95" y="25" font-size="10" fill="#9ca3af">50</text>
                            <text x="165" y="115" font-size="10" fill="#9ca3af">100</text>
                        </svg>
                        
                        <div class="trust-score-display">
                            <div class="trust-score-number" style="color: ${color};">
                                ${Math.round(this.score)}
                            </div>
                            <div class="trust-score-label">out of 100</div>
                        </div>
                    </div>
                    
                    <div class="trust-score-details">
                        <div class="trust-score-status" style="color: ${color};">
                            ${status}
                        </div>
                        <p class="trust-score-description">
                            ${description}
                        </p>
                        
                        <div class="trust-score-breakdown">
                            <h4>Score Components:</h4>
                            <div class="score-factors">
                                ${this.renderScoreFactors()}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="trust-score-legend">
                    <div class="legend-item">
                        <span class="legend-color" style="background: #ef4444;"></span>
                        <span>Low Trust (0-30)</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background: #f59e0b;"></span>
                        <span>Moderate (31-60)</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background: #10b981;"></span>
                        <span>High Trust (61-100)</span>
                    </div>
                </div>
            </div>
        `;
        
        this.container = container;
        
        // Animate the score after render
        setTimeout(() => this.animateScore(), 100);
        
        return container;
    }

    getScoreDetails(score) {
        if (score >= 61) {
            return {
                color: '#10b981',
                status: 'High Trustworthiness',
                description: 'This article appears to be from a credible source with good journalistic standards.'
            };
        } else if (score >= 31) {
            return {
                color: '#f59e0b',
                status: 'Moderate Trustworthiness',
                description: 'This article has some credibility concerns. Verify key claims with additional sources.'
            };
        } else {
            return {
                color: '#ef4444',
                status: 'Low Trustworthiness',
                description: 'This article has significant credibility issues. Exercise caution and seek alternative sources.'
            };
        }
    }

    calculateArcLength(score) {
        // Arc length is 251.33 (half circle)
        return (score / 100) * 251.33;
    }

    renderScoreFactors() {
        // These would come from the actual analysis data
        const factors = [
            { name: 'Source Credibility', impact: '+25', positive: true },
            { name: 'Author Reputation', impact: '+15', positive: true },
            { name: 'Factual Accuracy', impact: '+20', positive: true },
            { name: 'Bias Level', impact: '-10', positive: false },
            { name: 'Manipulation Tactics', impact: '-5', positive: false }
        ];
        
        return factors.map(factor => `
            <div class="score-factor">
                <span class="factor-name">${factor.name}</span>
                <span class="factor-impact ${factor.positive ? 'positive' : 'negative'}">
                    ${factor.impact}
                </span>
            </div>
        `).join('');
    }

    animateScore() {
        if (!this.container) return;
        
        const numberEl = this.container.querySelector('.trust-score-number');
        const arcEl = this.container.querySelector('.trust-score-arc');
        
        if (numberEl && arcEl) {
            // Animate number
            let current = 0;
            const target = this.score;
            const increment = target / 30; // 30 frames
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                numberEl.textContent = Math.round(current);
            }, 30);
            
            // Arc animation is handled by CSS transition
        }
    }

    update(score) {
        this.score = score;
        if (this.container) {
            const parent = this.container.parentNode;
            const newContainer = this.render(score);
            parent.replaceChild(newContainer, this.container);
        }
    }
}

// Export and register with UI controller
window.TrustScore = TrustScore;

// Auto-register when UI controller is available
if (window.UI) {
    window.UI.registerComponent('trustScore', new TrustScore());
}
