// static/js/components/clickbait-detector.js

class ClickbaitDetector {
    constructor() {
        this.container = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'clickbait-detector-container analysis-card';
        
        const clickbaitScore = data.clickbait_score || 0;
        const isBasicPlan = !data.is_pro;
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">🎣</span>
                <span>Clickbait Detection</span>
                ${!isBasicPlan ? '<span class="pro-indicator">PRO</span>' : ''}
            </div>
            
            <div class="clickbait-content">
                ${isBasicPlan ? this.renderBasicClickbait(clickbaitScore) : this.renderProClickbait(clickbaitScore, data)}
            </div>
        `;
        
        this.container = container;
        
        // Animate gauge
        setTimeout(() => this.animateGauge(), 100);
        
        return container;
    }

    renderBasicClickbait(score) {
        return `
            <div class="clickbait-basic">
                <p class="clickbait-basic-text">
                    Clickbait likelihood: <strong>${this.getClickbaitLevel(score)}</strong>
                </p>
                <div class="upgrade-prompt compact">
                    <span class="lock-icon">🔒</span>
                    <p>Get detailed clickbait analysis with Pro</p>
                </div>
            </div>
        `;
    }

    renderProClickbait(score, data) {
        const { color, status, description } = this.getClickbaitDetails(score);
        const indicators = data.clickbait_indicators || [];
        
        return `
            <!-- Clickbait Gauge -->
            <div class="clickbait-gauge-section">
                <div class="gauge-container">
                    <svg class="clickbait-gauge" width="200" height="140" viewBox="0 0 200 140">
                        <!-- Background -->
                        <defs>
                            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
                                <stop offset="50%" style="stop-color:#f59e0b;stop-opacity:1" />
                                <stop offset="100%" style="stop-color:#ef4444;stop-opacity:1" />
                            </linearGradient>
                        </defs>
                        
                        <!-- Background arc -->
                        <path 
                            d="M 20 120 A 80 80 0 0 1 180 120" 
                            fill="none" 
                            stroke="#e5e7eb" 
                            stroke-width="20"
                            stroke-linecap="round"
                        />
                        
                        <!-- Color arc -->
                        <path 
                            d="M 20 120 A 80 80 0 0 1 180 120" 
                            fill="none" 
                            stroke="url(#gaugeGradient)" 
                            stroke-width="20"
                            stroke-linecap="round"
                        />
                        
                        <!-- Needle -->
                        <g class="gauge-needle" transform="translate(100, 120)">
                            <circle r="8" fill="#374151"/>
                            <path 
                                d="M -3 0 L 0 -70 L 3 0 Z" 
                                fill="#374151"
                                transform="rotate(${this.calculateNeedleRotation(score)})"
                            />
                        </g>
                        
                        <!-- Labels -->
                        <text x="30" y="135" text-anchor="middle" font-size="12" fill="#6b7280">Low</text>
                        <text x="100" y="30" text-anchor="middle" font-size="12" fill="#6b7280">Medium</text>
                        <text x="170" y="135" text-anchor="middle" font-size="12" fill="#6b7280">High</text>
                    </svg>
                    
                    <div class="gauge-display">
                        <div class="gauge-score" style="color: ${color};">
                            ${Math.round(score)}%
                        </div>
                        <div class="gauge-status" style="color: ${color};">
                            ${status}
                        </div>
                    </div>
                </div>
                
                <p class="clickbait-description">${description}</p>
            </div>

            <!-- Clickbait Indicators -->
            ${indicators.length > 0 ? `
            <div class="clickbait-indicators">
                <h4>Clickbait Indicators Found:</h4>
                <div class="indicators-grid">
                    ${indicators.map(indicator => this.renderIndicator(indicator)).join('')}
                </div>
            </div>
            ` : ''}

            <!-- Title Analysis -->
            ${data.title_analysis ? `
            <div class="title-analysis">
                <h4>📰 Title Analysis</h4>
                <div class="title-breakdown">
                    <div class="title-metric">
                        <span class="metric-label">Sensationalism:</span>
                        <div class="mini-bar">
                            <div class="mini-fill" style="width: ${data.title_analysis.sensationalism || 0}%; background: #ef4444;"></div>
                        </div>
                        <span class="metric-value">${data.title_analysis.sensationalism || 0}%</span>
                    </div>
                    <div class="title-metric">
                        <span class="metric-label">Curiosity Gap:</span>
                        <div class="mini-bar">
                            <div class="mini-fill" style="width: ${data.title_analysis.curiosity_gap || 0}%; background: #f59e0b;"></div>
                        </div>
                        <span class="metric-value">${data.title_analysis.curiosity_gap || 0}%</span>
                    </div>
                    <div class="title-metric">
                        <span class="metric-label">Emotional Words:</span>
                        <div class="mini-bar">
                            <div class="mini-fill" style="width: ${data.title_analysis.emotional_words || 0}%; background: #8b5cf6;"></div>
                        </div>
                        <span class="metric-value">${data.title_analysis.emotional_words || 0}%</span>
                    </div>
                </div>
            </div>
            ` : ''}

            <!-- Recommendations -->
            ${score > 50 ? `
            <div class="clickbait-recommendations">
                <h4>⚠️ Reader Advisory</h4>
                <ul>
                    ${score > 70 ? '<li>This article shows strong clickbait characteristics</li>' : ''}
                    <li>Be aware of potential sensationalism in the content</li>
                    <li>Verify key claims with additional sources</li>
                    <li>Consider the publication\'s motivation for using such tactics</li>
                </ul>
            </div>
            ` : ''}
        `;
    }

    getClickbaitLevel(score) {
        if (score < 30) return 'Low';
        if (score < 70) return 'Moderate';
        return 'High';
    }

    getClickbaitDetails(score) {
        if (score < 30) {
            return {
                color: '#10b981',
                status: 'Low Clickbait',
                description: 'This article uses straightforward, informative headlines without sensationalism.'
            };
        } else if (score < 70) {
            return {
                color: '#f59e0b',
                status: 'Moderate Clickbait',
                description: 'This article uses some attention-grabbing techniques but maintains reasonable accuracy.'
            };
        } else {
            return {
                color: '#ef4444',
                status: 'High Clickbait',
                description: 'This article heavily relies on sensationalism and curiosity gaps to attract clicks.'
            };
        }
    }

    calculateNeedleRotation(score) {
        // Convert 0-100 score to -90 to +90 degrees
        return (score / 100) * 180 - 90;
    }

    renderIndicator(indicator) {
        const typeIcons = {
            'sensational_language': '🔥',
            'curiosity_gap': '❓',
            'emotional_appeal': '😱',
            'exaggeration': '📢',
            'misleading_headline': '⚠️',
            'lists_numbers': '🔢',
            'urgent_language': '⏰',
            'shocking_reveal': '😲'
        };
        
        return `
            <div class="indicator-item">
                <span class="indicator-icon">${typeIcons[indicator.type] || '📌'}</span>
                <div class="indicator-details">
                    <div class="indicator-name">${indicator.name}</div>
                    <div class="indicator-description">${indicator.description}</div>
                </div>
            </div>
        `;
    }

    animateGauge() {
        const needle = this.container?.querySelector('.gauge-needle');
        const score = this.container?.querySelector('.gauge-score');
        
        if (needle) {
            const transform = needle.getAttribute('transform');
            const rotation = needle.querySelector('path').getAttribute('transform');
            
            // Reset needle position
            needle.querySelector('path').setAttribute('transform', 'rotate(-90)');
            
            // Animate to final position
            setTimeout(() => {
                needle.querySelector('path').style.transition = 'transform 1s ease-out';
                needle.querySelector('path').setAttribute('transform', rotation);
            }, 50);
        }
        
        // Animate score number
        if (score) {
            const target = parseInt(score.textContent);
            let current = 0;
            const increment = target / 30;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                score.textContent = Math.round(current) + '%';
            }, 30);
        }
        
        // Animate mini bars
        const miniFills = this.container?.querySelectorAll('.mini-fill');
        miniFills?.forEach((fill, index) => {
            const width = fill.style.width;
            fill.style.width = '0%';
            setTimeout(() => {
                fill.style.transition = 'width 0.8s ease-out';
                fill.style.width = width;
            }, 100 + (index * 100));
        });
    }
}

// Export and register with UI controller
window.ClickbaitDetector = ClickbaitDetector;

// Auto-register when UI controller is available
if (window.UI) {
    window.UI.registerComponent('clickbaitDetector', new ClickbaitDetector());
}
