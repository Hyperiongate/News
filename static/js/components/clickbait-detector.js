// static/js/components/clickbait-detector.js
// Enhanced Clickbait Detector with Detailed Analysis

class ClickbaitDetector {
    constructor() {
        this.container = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'clickbait-detector-container analysis-card';
        
        const clickbaitScore = data.clickbait_score || 0;
        const analysis = data.clickbait_analysis || {};
        const isBasicPlan = !data.is_pro;
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">🎣</span>
                <span>Clickbait Detection</span>
                ${!isBasicPlan ? '<span class="pro-indicator">PRO</span>' : ''}
            </div>
            
            <div class="clickbait-content">
                ${isBasicPlan ? this.renderBasicClickbait(clickbaitScore) : this.renderProClickbait(clickbaitScore, analysis)}
            </div>
        `;
        
        this.container = container;
        
        // Initialize animations
        setTimeout(() => this.initializeAnimations(), 100);
        
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

    renderProClickbait(score, analysis) {
        const level = this.getClickbaitDetails(score);
        const indicators = analysis.indicators || [];
        const titleAnalysis = analysis.title_analysis || {};
        const tactics = analysis.tactics || [];
        
        return `
            <!-- Clickbait Overview -->
            <div class="clickbait-overview">
                <h4>Headline Manipulation Analysis</h4>
                <p class="analysis-explanation">
                    Our system detects 15+ clickbait indicators including emotional manipulation, 
                    curiosity gaps, sensationalism, misleading claims, and exaggeration patterns.
                </p>
            </div>

            <!-- Main Gauge Display -->
            <div class="clickbait-gauge-section">
                <div class="gauge-wrapper">
                    <div class="gauge-container">
                        <svg class="clickbait-gauge" viewBox="0 0 200 120">
                            <defs>
                                <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
                                    <stop offset="50%" style="stop-color:#f59e0b;stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:#ef4444;stop-opacity:1" />
                                </linearGradient>
                            </defs>
                            
                            <!-- Background arc -->
                            <path d="M 30 100 A 70 70 0 0 1 170 100" 
                                  fill="none" 
                                  stroke="#e5e7eb" 
                                  stroke-width="20"/>
                            
                            <!-- Score arc -->
                            <path d="M 30 100 A 70 70 0 0 1 170 100" 
                                  fill="none" 
                                  stroke="url(#gaugeGradient)" 
                                  stroke-width="20"
                                  stroke-dasharray="220"
                                  stroke-dashoffset="${220 - (score / 100 * 220)}"
                                  class="gauge-fill"
                                  stroke-linecap="round"/>
                            
                            <!-- Needle -->
                            <g class="gauge-needle" transform="rotate(${-90 + (score / 100 * 180)}, 100, 100)">
                                <line x1="100" y1="100" x2="100" y2="40" stroke="#1f2937" stroke-width="3"/>
                                <circle cx="100" cy="100" r="5" fill="#1f2937"/>
                            </g>
                            
                            <!-- Score text -->
                            <text x="100" y="90" text-anchor="middle" font-size="32" font-weight="bold" fill="#1f2937">
                                ${score}%
                            </text>
                            <text x="100" y="110" text-anchor="middle" font-size="14" fill="#6b7280">
                                ${level.label}
                            </text>
                        </svg>
                    </div>
                    
                    <div class="gauge-interpretation">
                        <div class="level-indicator ${level.class}">
                            <span class="level-icon">${level.icon}</span>
                            <span class="level-text">${level.label} Clickbait</span>
                        </div>
                        <p class="level-description">${level.description}</p>
                    </div>
                </div>
            </div>

            <!-- Detected Indicators -->
            ${indicators.length > 0 ? `
                <div class="indicators-section">
                    <h4>Clickbait Indicators Detected</h4>
                    <div class="indicators-grid">
                        ${indicators.map(indicator => this.renderIndicator(indicator)).join('')}
                    </div>
                </div>
            ` : ''}

            <!-- Title Analysis -->
            ${Object.keys(titleAnalysis).length > 0 ? `
                <div class="title-analysis-section">
                    <h4>Headline Analysis Breakdown</h4>
                    ${this.renderTitleAnalysis(titleAnalysis)}
                </div>
            ` : ''}

            <!-- Clickbait Tactics -->
            ${tactics.length > 0 ? `
                <div class="tactics-section">
                    <h4>Manipulation Tactics Used</h4>
                    <div class="tactics-list">
                        ${tactics.map(tactic => this.renderTactic(tactic)).join('')}
                    </div>
                </div>
            ` : ''}

            <!-- Recommendations -->
            ${score > 40 ? `
                <div class="recommendations-section">
                    <h4>Reader Advisory</h4>
                    <div class="recommendations-box">
                        ${this.getRecommendations(score, indicators)}
                    </div>
                </div>
            ` : ''}

            <!-- How We Detect Clickbait -->
            <div class="methodology-section">
                <h4>How We Detect Clickbait</h4>
                <div class="methodology-grid">
                    <div class="method-item">
                        <span class="method-icon">🧠</span>
                        <span class="method-name">AI Pattern Analysis</span>
                        <p class="method-desc">Machine learning models trained on thousands of clickbait examples</p>
                    </div>
                    <div class="method-item">
                        <span class="method-icon">📊</span>
                        <span class="method-name">Statistical Analysis</span>
                        <p class="method-desc">Word frequency, punctuation patterns, and structural indicators</p>
                    </div>
                    <div class="method-item">
                        <span class="method-icon">🎯</span>
                        <span class="method-name">Psychological Tactics</span>
                        <p class="method-desc">Detection of curiosity gaps, fear appeals, and emotional triggers</p>
                    </div>
                    <div class="method-item">
                        <span class="method-icon">📝</span>
                        <span class="method-name">Linguistic Analysis</span>
                        <p class="method-desc">Examination of superlatives, vague language, and exaggerations</p>
                    </div>
                </div>
            </div>
        `;
    }

    renderIndicator(indicator) {
        const indicatorInfo = this.getIndicatorInfo(indicator.type || indicator);
        
        return `
            <div class="indicator-card ${indicatorInfo.severity}">
                <div class="indicator-header">
                    <span class="indicator-icon">${indicatorInfo.icon}</span>
                    <span class="indicator-name">${indicator.name || indicatorInfo.name}</span>
                    <span class="indicator-severity severity-${indicatorInfo.severity}">${indicatorInfo.severity}</span>
                </div>
                <p class="indicator-description">${indicatorInfo.description}</p>
                ${indicator.example ? `
                    <div class="indicator-example">
                        <strong>Example found:</strong> "${indicator.example}"
                    </div>
                ` : ''}
                ${indicator.count && indicator.count > 1 ? `
                    <div class="indicator-count">Found ${indicator.count} times</div>
                ` : ''}
            </div>
        `;
    }

    renderTitleAnalysis(analysis) {
        const metrics = [
            {
                name: 'Sensationalism',
                value: analysis.sensationalism || 0,
                icon: '🔥',
                description: 'Use of extreme or exaggerated language'
            },
            {
                name: 'Curiosity Gap',
                value: analysis.curiosity_gap || 0,
                icon: '❓',
                description: 'Withholding key information to force clicks'
            },
            {
                name: 'Emotional Triggers',
                value: analysis.emotional_triggers || 0,
                icon: '❤️',
                description: 'Words designed to provoke strong emotions'
            },
            {
                name: 'Urgency/FOMO',
                value: analysis.urgency || 0,
                icon: '⏰',
                description: 'Creating false sense of urgency'
            },
            {
                name: 'Vague Language',
                value: analysis.vagueness || 0,
                icon: '🌫️',
                description: 'Unclear or ambiguous wording'
            },
            {
                name: 'Exaggeration',
                value: analysis.exaggeration || 0,
                icon: '📈',
                description: 'Overstating facts or numbers'
            }
        ];
        
        return `
            <div class="title-metrics-grid">
                ${metrics.map(metric => `
                    <div class="title-metric">
                        <div class="metric-header">
                            <span class="metric-icon">${metric.icon}</span>
                            <span class="metric-name">${metric.name}</span>
                        </div>
                        <div class="metric-bar-container">
                            <div class="metric-bar">
                                <div class="metric-fill" style="width: ${metric.value}%; background: ${this.getMetricColor(metric.value)}"></div>
                            </div>
                            <span class="metric-value">${metric.value}%</span>
                        </div>
                        <p class="metric-description">${metric.description}</p>
                    </div>
                `).join('')}
            </div>
            
            ${analysis.headline_issues && analysis.headline_issues.length > 0 ? `
                <div class="headline-issues">
                    <h5>Specific Issues Found</h5>
                    <ul class="issues-list">
                        ${analysis.headline_issues.map(issue => `<li>${issue}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
    }

    renderTactic(tactic) {
        const tacticInfo = {
            'curiosity_gap': {
                icon: '🕳️',
                name: 'Curiosity Gap',
                description: 'Headline teases information without revealing it'
            },
            'emotional_manipulation': {
                icon: '😱',
                name: 'Emotional Manipulation',
                description: 'Uses shock, fear, or outrage to drive clicks'
            },
            'misleading_claim': {
                icon: '🎭',
                name: 'Misleading Claims',
                description: 'Implies something not supported by content'
            },
            'false_urgency': {
                icon: '⚡',
                name: 'False Urgency',
                description: 'Creates artificial time pressure'
            },
            'listicle': {
                icon: '📋',
                name: 'Listicle Format',
                description: 'Uses numbered lists to attract clicks'
            },
            'superlatives': {
                icon: '🌟',
                name: 'Extreme Superlatives',
                description: 'Uses words like "shocking", "amazing", "unbelievable"'
            }
        };
        
        const info = tacticInfo[tactic.type] || {
            icon: '📌',
            name: tactic.name || tactic,
            description: tactic.description || 'Clickbait tactic detected'
        };
        
        return `
            <div class="tactic-card">
                <div class="tactic-icon">${info.icon}</div>
                <div class="tactic-content">
                    <div class="tactic-name">${info.name}</div>
                    <p class="tactic-description">${info.description}</p>
                    ${tactic.example ? `
                        <div class="tactic-example">
                            <strong>Example:</strong> "${tactic.example}"
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    getClickbaitLevel(score) {
        if (score < 30) return 'Low';
        if (score < 60) return 'Moderate';
        if (score < 80) return 'High';
        return 'Extreme';
    }

    getClickbaitDetails(score) {
        if (score < 30) {
            return {
                label: 'Low',
                class: 'low',
                icon: '✅',
                description: 'This headline uses straightforward language without sensationalism or manipulation tactics.'
            };
        } else if (score < 60) {
            return {
                label: 'Moderate',
                class: 'moderate',
                icon: '⚠️',
                description: 'Some clickbait elements detected. The headline may exaggerate or use emotional triggers.'
            };
        } else if (score < 80) {
            return {
                label: 'High',
                class: 'high',
                icon: '🚨',
                description: 'Significant clickbait tactics used. Be cautious of sensationalism and misleading claims.'
            };
        } else {
            return {
                label: 'Extreme',
                class: 'extreme',
                icon: '❗',
                description: 'Heavy use of clickbait tactics. Content likely does not match the sensational headline.'
            };
        }
    }

    getIndicatorInfo(type) {
        const indicators = {
            'all_caps': {
                name: 'ALL CAPS Words',
                icon: '🔤',
                severity: 'medium',
                description: 'Excessive use of capital letters to grab attention'
            },
            'excessive_punctuation': {
                name: 'Excessive Punctuation',
                icon: '❗❓',
                severity: 'medium',
                description: 'Multiple exclamation marks or question marks'
            },
            'you_wont_believe': {
                name: '"You Won\'t Believe"',
                icon: '😮',
                severity: 'high',
                description: 'Classic clickbait phrase that overpromises'
            },
            'number_list': {
                name: 'Numbered List',
                icon: '🔢',
                severity: 'low',
                description: 'Uses numbers to create list-based content'
            },
            'shocking_words': {
                name: 'Shock Words',
                icon: '💥',
                severity: 'high',
                description: 'Words like "shocking", "devastating", "mind-blowing"'
            },
            'vague_pronouns': {
                name: 'Vague References',
                icon: '👤',
                severity: 'medium',
                description: 'Uses "this", "what happened", without clarity'
            },
            'curiosity_gap': {
                name: 'Curiosity Gap',
                icon: '🕳️',
                severity: 'high',
                description: 'Withholds key information to force clicks'
            },
            'emotional_trigger': {
                name: 'Emotional Triggers',
                icon: '😡',
                severity: 'medium',
                description: 'Targets emotions like anger, fear, or outrage'
            }
        };
        
        return indicators[type] || {
            name: type,
            icon: '📌',
            severity: 'medium',
            description: 'Clickbait indicator detected'
        };
    }

    getRecommendations(score, indicators) {
        const recommendations = [];
        
        if (score > 70) {
            recommendations.push('⚠️ This article uses heavy clickbait tactics. The actual content may not match the sensational headline.');
        }
        
        if (indicators.some(i => i.type === 'curiosity_gap')) {
            recommendations.push('🕳️ The headline deliberately withholds information. Be prepared for disappointment.');
        }
        
        if (indicators.some(i => i.type === 'emotional_trigger')) {
            recommendations.push('😡 Emotional manipulation detected. Read with a critical mindset.');
        }
        
        recommendations.push('💡 Always verify sensational claims with multiple sources.');
        recommendations.push('🔍 Check if the article content actually delivers on the headline\'s promise.');
        
        return `
            <ul class="recommendations-list">
                ${recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        `;
    }

    getMetricColor(value) {
        if (value < 30) return '#10b981';
        if (value < 60) return '#f59e0b';
        return '#ef4444';
    }

    initializeAnimations() {
        // Animate gauge
        const gaugeFill = this.container.querySelector('.gauge-fill');
        if (gaugeFill) {
            const dashoffset = gaugeFill.getAttribute('stroke-dashoffset');
            gaugeFill.setAttribute('stroke-dashoffset', '220');
            setTimeout(() => {
                gaugeFill.style.transition = 'stroke-dashoffset 1.5s ease-out';
                gaugeFill.setAttribute('stroke-dashoffset', dashoffset);
            }, 100);
        }
        
        // Animate needle
        const needle = this.container.querySelector('.gauge-needle');
        if (needle) {
            const transform = needle.getAttribute('transform');
            needle.setAttribute('transform', 'rotate(-90, 100, 100)');
            setTimeout(() => {
                needle.style.transition = 'transform 1.5s ease-out';
                needle.setAttribute('transform', transform);
            }, 100);
        }
        
        // Animate metric bars
        const metricFills = this.container.querySelectorAll('.metric-fill');
        metricFills.forEach(fill => {
            const width = fill.style.width;
            fill.style.width = '0';
            setTimeout(() => {
                fill.style.transition = 'width 1s ease-out';
                fill.style.width = width;
            }, 200);
        });
    }
}

// Export and register
window.ClickbaitDetector = ClickbaitDetector;

// Auto-register with UI controller
document.addEventListener('DOMContentLoaded', () => {
    if (window.UI) {
        window.UI.registerComponent('clickbaitDetector', new ClickbaitDetector());
    }
});
