// static/js/components/bias-analysis.js

class BiasAnalysis {
    constructor() {
        this.container = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'bias-analysis-container analysis-card';
        
        const bias = data.bias_analysis || {};
        const isBasicPlan = !data.is_pro;
        
        // For basic plan, show limited info
        if (isBasicPlan) {
            container.innerHTML = this.renderBasicBias(bias);
        } else {
            container.innerHTML = this.renderProBias(bias, data);
        }
        
        this.container = container;
        
        // Animate the bias indicator
        setTimeout(() => this.animateBiasIndicator(), 100);
        
        return container;
    }

    renderBasicBias(bias) {
        const overallBias = bias.overall_bias || 'Unknown';
        const biasScore = this.calculateBiasScore(bias);
        
        return `
            <div class="analysis-header">
                <span class="analysis-icon">⚖️</span>
                <span>Bias Analysis</span>
            </div>
            
            <div class="bias-content">
                <div class="bias-summary">
                    <p class="bias-basic-text">
                        Overall bias detected: <strong>${overallBias}</strong>
                    </p>
                    <div class="upgrade-prompt">
                        <span class="lock-icon">🔒</span>
                        <p>Unlock detailed bias analysis including political lean, manipulation tactics, and emotional language detection with Pro plan.</p>
                        <button class="upgrade-btn" onclick="window.pricingDropdown?.selectPlan('pro')">
                            Upgrade to Pro
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    renderProBias(bias, data) {
        const biasScore = this.calculateBiasScore(bias);
        const politicalLean = bias.political_lean || 0; // -100 to +100
        const manipulationTactics = bias.manipulation_tactics || [];
        
        return `
            <div class="analysis-header">
                <span class="analysis-icon">⚖️</span>
                <span>Detailed Bias Analysis</span>
                <span class="pro-indicator">PRO</span>
            </div>
            
            <div class="bias-content">
                <!-- Political Bias Scale -->
                <div class="political-bias-section">
                    <h4>Political Lean</h4>
                    <div class="bias-scale-container">
                        <div class="bias-scale">
                            <div class="bias-scale-track"></div>
                            <div class="bias-scale-center"></div>
                            <div class="bias-indicator" style="left: ${this.calculateIndicatorPosition(politicalLean)}%;">
                                <div class="bias-indicator-dot"></div>
                                <div class="bias-indicator-label">${this.getPoliticalLeanLabel(politicalLean)}</div>
                            </div>
                        </div>
                        <div class="bias-scale-labels">
                            <span class="scale-label left">Far Left</span>
                            <span class="scale-label">Left</span>
                            <span class="scale-label center">Center</span>
                            <span class="scale-label">Right</span>
                            <span class="scale-label right">Far Right</span>
                        </div>
                    </div>
                    <p class="bias-description">${this.getPoliticalDescription(politicalLean)}</p>
                </div>

                <!-- Bias Metrics -->
                <div class="bias-metrics">
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-icon">🎯</span>
                            <span>Objectivity Score</span>
                        </div>
                        <div class="metric-value">${bias.objectivity_score || 0}%</div>
                        <div class="metric-bar">
                            <div class="metric-fill" style="width: ${bias.objectivity_score || 0}%; background: #10b981;"></div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-icon">💭</span>
                            <span>Opinion vs Facts</span>
                        </div>
                        <div class="metric-value">${bias.opinion_percentage || 0}% Opinion</div>
                        <div class="metric-bar">
                            <div class="metric-fill" style="width: ${bias.opinion_percentage || 0}%; background: #f59e0b;"></div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-icon">😤</span>
                            <span>Emotional Language</span>
                        </div>
                        <div class="metric-value">${this.getEmotionalLevel(bias.emotional_score)}</div>
                        <div class="metric-bar">
                            <div class="metric-fill" style="width: ${bias.emotional_score || 0}%; background: #ef4444;"></div>
                        </div>
                    </div>
                </div>

                <!-- Manipulation Tactics -->
                ${manipulationTactics.length > 0 ? `
                <div class="manipulation-section">
                    <h4>⚠️ Manipulation Tactics Detected</h4>
                    <div class="tactics-list">
                        ${manipulationTactics.map(tactic => `
                            <div class="tactic-item">
                                <span class="tactic-icon">${this.getTacticIcon(tactic.type)}</span>
                                <div class="tactic-details">
                                    <div class="tactic-name">${tactic.name}</div>
                                    <div class="tactic-description">${tactic.description}</div>
                                    ${tactic.example ? `<div class="tactic-example">"${tactic.example}"</div>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}

                <!-- Loaded Language Examples -->
                ${bias.loaded_phrases && bias.loaded_phrases.length > 0 ? `
                <div class="loaded-language-section">
                    <h4>🔥 Loaded Language Examples</h4>
                    <div class="loaded-phrases">
                        ${bias.loaded_phrases.map(phrase => `
                            <div class="loaded-phrase">
                                <span class="phrase-text">"${phrase.text}"</span>
                                <span class="phrase-type">${phrase.type}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}

                <!-- AI Analysis Summary -->
                ${bias.ai_summary ? `
                <div class="ai-summary">
                    <h4>🤖 AI Analysis Summary</h4>
                    <p>${bias.ai_summary}</p>
                </div>
                ` : ''}
            </div>
        `;
    }

    calculateBiasScore(bias) {
        // Simple calculation based on available metrics
        const objectivity = bias.objectivity_score || 50;
        const opinionWeight = 100 - (bias.opinion_percentage || 50);
        const emotionalWeight = 100 - (bias.emotional_score || 50);
        
        return Math.round((objectivity + opinionWeight + emotionalWeight) / 3);
    }

    calculateIndicatorPosition(lean) {
        // Convert -100 to +100 scale to 0-100% position
        return ((lean + 100) / 200) * 100;
    }

    getPoliticalLeanLabel(lean) {
        if (lean < -60) return 'Far Left';
        if (lean < -20) return 'Left';
        if (lean < 20) return 'Center';
        if (lean < 60) return 'Right';
        return 'Far Right';
    }

    getPoliticalDescription(lean) {
        if (Math.abs(lean) < 20) {
            return 'This article maintains a relatively balanced political perspective.';
        } else if (lean < -20) {
            return 'This article shows a left-leaning political bias in its coverage and framing.';
        } else {
            return 'This article shows a right-leaning political bias in its coverage and framing.';
        }
    }

    getEmotionalLevel(score) {
        if (!score) return 'Low';
        if (score < 30) return 'Low';
        if (score < 60) return 'Moderate';
        return 'High';
    }

    getTacticIcon(type) {
        const icons = {
            'strawman': '🎯',
            'ad_hominem': '👤',
            'false_dilemma': '⚡',
            'appeal_emotion': '❤️',
            'loaded_question': '❓',
            'cherry_picking': '🍒',
            'bandwagon': '🚂',
            'slippery_slope': '🎿',
            'default': '⚠️'
        };
        return icons[type] || icons.default;
    }

    animateBiasIndicator() {
        const indicator = this.container?.querySelector('.bias-indicator');
        if (indicator) {
            indicator.style.opacity = '0';
            indicator.style.transform = 'translateX(-50%) translateY(10px)';
            setTimeout(() => {
                indicator.style.transition = 'all 0.8s ease-out';
                indicator.style.opacity = '1';
                indicator.style.transform = 'translateX(-50%) translateY(0)';
            }, 50);
        }

        // Animate metric bars
        const metricFills = this.container?.querySelectorAll('.metric-fill');
        metricFills?.forEach((fill, index) => {
            const width = fill.style.width;
            fill.style.width = '0%';
            setTimeout(() => {
                fill.style.transition = 'width 1s ease-out';
                fill.style.width = width;
            }, 100 + (index * 100));
        });
    }
}

// Export and register with UI controller
window.BiasAnalysis = BiasAnalysis;

// Auto-register when UI controller is available
if (window.UI) {
    window.UI.registerComponent('biasAnalysis', new BiasAnalysis());
}
