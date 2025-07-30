// static/js/components/clickbait-detector.js
// Enhanced Clickbait Detector with Detailed Analysis

class ClickbaitDetector {
    constructor() {
        this.container = null;
        this.indicators = {
            curiosityGap: {
                name: 'Curiosity Gap',
                description: 'Creates information gap to force clicks',
                weight: 3,
                patterns: ['you won\'t believe', 'what happened next', 'shocking truth', 'this one trick']
            },
            emotionalTriggers: {
                name: 'Emotional Manipulation',
                description: 'Uses strong emotions to drive engagement',
                weight: 2.5,
                patterns: ['shocking', 'heartbreaking', 'outrageous', 'disgusting', 'amazing']
            },
            exaggeration: {
                name: 'Exaggeration',
                description: 'Overstates importance or impact',
                weight: 2,
                patterns: ['destroyed', 'obliterated', 'perfect', 'ultimate', 'life-changing']
            },
            listicles: {
                name: 'Numbered Lists',
                description: 'Uses numbers to promise digestible content',
                weight: 1.5,
                patterns: [/\d+\s+(ways|reasons|things|tips|facts)/i]
            },
            urgency: {
                name: 'False Urgency',
                description: 'Creates artificial time pressure',
                weight: 2,
                patterns: ['breaking', 'urgent', 'right now', 'before it\'s gone']
            },
            personalAddress: {
                name: 'Direct Address',
                description: 'Speaks directly to reader',
                weight: 1,
                patterns: ['you', 'your', 'you\'re']
            }
        };
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'clickbait-detector-container analysis-card';
        
        const analysis = this.performDetailedAnalysis(data);
        const isBasicPlan = !data.is_pro;
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">🎣</span>
                <span>Clickbait Detection</span>
                ${!isBasicPlan ? '<span class="pro-indicator">PRO</span>' : ''}
            </div>
            
            <div class="clickbait-content">
                ${isBasicPlan ? this.renderBasicClickbait(analysis) : this.renderProClickbait(analysis)}
            </div>
        `;
        
        this.container = container;
        
        // Initialize animations
        if (!isBasicPlan) {
            setTimeout(() => this.initializeGauge(analysis.score), 100);
        }
        
        return container;
    }

    performDetailedAnalysis(data) {
        const title = data.article?.title || '';
        const content = data.article?.content || '';
        
        // Analyze title for clickbait indicators
        const detectedIndicators = [];
        let totalScore = 0;
        
        Object.entries(this.indicators).forEach(([key, indicator]) => {
            const detected = this.detectIndicator(title, indicator);
            if (detected.found) {
                detectedIndicators.push({
                    ...indicator,
                    key: key,
                    matches: detected.matches,
                    score: detected.score
                });
                totalScore += detected.score;
            }
        });
        
        // Additional analysis
        const titleAnalysis = {
            length: title.length,
            capitalizedWords: (title.match(/[A-Z][A-Z]+/g) || []).length,
            punctuation: (title.match(/[!?]/g) || []).length,
            hasNumbers: /\d/.test(title),
            hasQuotes: /["']/.test(title),
            wordCount: title.split(/\s+/).length
        };
        
        // Tactics analysis
        const tactics = this.analyzeTactics(title, content);
        
        // Calculate final score (0-100)
        const clickbaitScore = Math.min(100, Math.round(totalScore * 10));
        
        return {
            score: clickbaitScore,
            indicators: detectedIndicators,
            titleAnalysis: titleAnalysis,
            tactics: tactics,
            recommendation: this.getRecommendation(clickbaitScore),
            examples: this.findExamples(title, detectedIndicators)
        };
    }

    detectIndicator(title, indicator) {
        let found = false;
        const matches = [];
        let score = 0;
        
        indicator.patterns.forEach(pattern => {
            if (pattern instanceof RegExp) {
                const match = title.match(pattern);
                if (match) {
                    found = true;
                    matches.push(match[0]);
                    score += indicator.weight;
                }
            } else {
                if (title.toLowerCase().includes(pattern.toLowerCase())) {
                    found = true;
                    matches.push(pattern);
                    score += indicator.weight;
                }
            }
        });
        
        return { found, matches, score };
    }

    analyzeTactics(title, content) {
        const tactics = [];
        
        // Withholding information
        if (title.includes('...') || title.includes('what') || title.includes('how')) {
            tactics.push({
                name: 'Information Withholding',
                description: 'Deliberately hides key information to force clicks',
                severity: 'high',
                example: this.extractExample(title, ['...', 'what', 'how'])
            });
        }
        
        // Superlatives
        const superlatives = ['best', 'worst', 'most', 'least', 'only'];
        const foundSuperlatives = superlatives.filter(s => 
            title.toLowerCase().includes(s)
        );
        if (foundSuperlatives.length > 0) {
            tactics.push({
                name: 'Superlative Abuse',
                description: 'Uses extreme descriptors without justification',
                severity: 'moderate',
                example: foundSuperlatives.join(', ')
            });
        }
        
        // Vague pronouns
        if (/\b(this|these|that|those)\b/i.test(title) && !content.includes(title)) {
            tactics.push({
                name: 'Vague References',
                description: 'Uses unclear pronouns to create mystery',
                severity: 'moderate',
                example: 'Uses "this" or "that" without clear reference'
            });
        }
        
        // ALL CAPS
        if (title.match(/\b[A-Z]{3,}\b/)) {
            tactics.push({
                name: 'Capitalization Abuse',
                description: 'Uses ALL CAPS for emphasis',
                severity: 'low',
                example: title.match(/\b[A-Z]{3,}\b/)[0]
            });
        }
        
        return tactics;
    }

    findExamples(title, indicators) {
        const examples = [];
        
        indicators.forEach(indicator => {
            if (indicator.matches.length > 0) {
                examples.push({
                    text: indicator.matches[0],
                    type: indicator.name,
                    context: this.getContextAroundMatch(title, indicator.matches[0])
                });
            }
        });
        
        return examples.slice(0, 3); // Top 3 examples
    }

    getContextAroundMatch(text, match) {
        const index = text.toLowerCase().indexOf(match.toLowerCase());
        if (index === -1) return text;
        
        const start = Math.max(0, index - 20);
        const end = Math.min(text.length, index + match.length + 20);
        
        let context = text.substring(start, end);
        if (start > 0) context = '...' + context;
        if (end < text.length) context = context + '...';
        
        return context;
    }

    getRecommendation(score) {
        if (score < 20) {
            return {
                level: 'minimal',
                text: 'This headline appears straightforward and informative.',
                action: 'Safe to read - minimal clickbait detected.'
            };
        } else if (score < 40) {
            return {
                level: 'low',
                text: 'Some attention-grabbing elements present but within normal bounds.',
                action: 'Generally trustworthy - proceed with normal skepticism.'
            };
        } else if (score < 60) {
            return {
                level: 'moderate',
                text: 'Notable clickbait tactics detected. Content may not match headline.',
                action: 'Read with caution - verify claims independently.'
            };
        } else if (score < 80) {
            return {
                level: 'high',
                text: 'Heavy use of manipulation tactics. High likelihood of disappointment.',
                action: 'Warning - expect exaggeration and missing context.'
            };
        } else {
            return {
                level: 'extreme',
                text: 'Extreme clickbait. Content unlikely to deliver on promises.',
                action: 'Not recommended - seek alternative sources.'
            };
        }
    }

    renderBasicClickbait(analysis) {
        const level = this.getClickbaitLevel(analysis.score);
        
        return `
            <div class="clickbait-basic">
                <p class="clickbait-basic-text">
                    Clickbait likelihood: <strong>${level}</strong>
                </p>
                <div class="simple-meter">
                    <div class="meter-fill ${level.toLowerCase()}" style="width: ${analysis.score}%"></div>
                </div>
                <p class="basic-recommendation">${analysis.recommendation.action}</p>
                <div class="upgrade-prompt compact">
                    <span class="lock-icon">🔒</span>
                    <p>Get detailed clickbait analysis with Pro</p>
                </div>
            </div>
        `;
    }

    renderProClickbait(analysis) {
        return `
            <div class="clickbait-pro">
                <h4>Headline Manipulation Analysis</h4>
                <p class="analysis-explanation">
                    Our AI detects ${Object.keys(this.indicators).length}+ clickbait indicators including emotional manipulation, 
                    curiosity gaps, and exaggeration patterns.
                </p>
                
                <!-- Visual Gauge -->
                <div class="clickbait-gauge-container">
                    <canvas id="clickbaitGauge" width="300" height="150"></canvas>
                    <div class="gauge-labels">
                        <span class="minimal">Minimal</span>
                        <span class="low">Low</span>
                        <span class="moderate">Moderate</span>
                        <span class="high">High</span>
                        <span class="extreme">Extreme</span>
                    </div>
                </div>
                
                <!-- Score Breakdown -->
                <div class="score-breakdown">
                    <h5>Clickbait Score: ${analysis.score}/100</h5>
                    <div class="recommendation-box ${analysis.recommendation.level}">
                        <p class="recommendation-text">${analysis.recommendation.text}</p>
                        <p class="recommendation-action">${analysis.recommendation.action}</p>
                    </div>
                </div>
                
                <!-- Detected Indicators -->
                ${this.renderIndicators(analysis.indicators)}
                
                <!-- Title Analysis -->
                ${this.renderTitleAnalysis(analysis.titleAnalysis)}
                
                <!-- Manipulation Tactics -->
                ${this.renderTactics(analysis.tactics)}
                
                <!-- Examples -->
                ${this.renderExamples(analysis.examples)}
                
                <!-- Reader Advisory -->
                <div class="reader-advisory">
                    <h5>How to Read This Article</h5>
                    <ul>
                        ${this.getReadingTips(analysis.score).map(tip => 
                            `<li>${tip}</li>`
                        ).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    renderIndicators(indicators) {
        if (indicators.length === 0) {
            return `
                <div class="indicators-section">
                    <h5>No Significant Clickbait Indicators Detected</h5>
                    <p>This headline appears to be straightforward and honest.</p>
                </div>
            `;
        }
        
        return `
            <div class="indicators-section">
                <h5>Detected Clickbait Indicators</h5>
                <div class="indicators-grid">
                    ${indicators.map(indicator => `
                        <div class="indicator-card">
                            <div class="indicator-header">
                                <span class="indicator-name">${indicator.name}</span>
                                <span class="indicator-score">+${indicator.score.toFixed(1)}</span>
                            </div>
                            <p class="indicator-description">${indicator.description}</p>
                            <div class="indicator-matches">
                                <span class="matches-label">Found:</span>
                                ${indicator.matches.map(match => 
                                    `<span class="match-chip">"${match}"</span>`
                                ).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderTitleAnalysis(analysis) {
        return `
            <div class="title-analysis-section">
                <h5>Headline Structure Analysis</h5>
                <div class="analysis-metrics">
                    <div class="metric">
                        <span class="metric-label">Length</span>
                        <span class="metric-value">${analysis.length} chars</span>
                        <span class="metric-status ${analysis.length > 100 ? 'warning' : 'good'}">
                            ${analysis.length > 100 ? 'Too long' : 'Good'}
                        </span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">ALL CAPS Words</span>
                        <span class="metric-value">${analysis.capitalizedWords}</span>
                        <span class="metric-status ${analysis.capitalizedWords > 1 ? 'warning' : 'good'}">
                            ${analysis.capitalizedWords > 1 ? 'Excessive' : 'Normal'}
                        </span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Punctuation (!?)</span>
                        <span class="metric-value">${analysis.punctuation}</span>
                        <span class="metric-status ${analysis.punctuation > 1 ? 'warning' : 'good'}">
                            ${analysis.punctuation > 1 ? 'Excessive' : 'Normal'}
                        </span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Contains Numbers</span>
                        <span class="metric-value">${analysis.hasNumbers ? 'Yes' : 'No'}</span>
                        <span class="metric-status neutral">
                            ${analysis.hasNumbers ? 'Listicle likely' : 'Standard'}
                        </span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Word Count</span>
                        <span class="metric-value">${analysis.wordCount}</span>
                        <span class="metric-status ${analysis.wordCount > 15 ? 'warning' : 'good'}">
                            ${analysis.wordCount > 15 ? 'Verbose' : 'Concise'}
                        </span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Has Quotes</span>
                        <span class="metric-value">${analysis.hasQuotes ? 'Yes' : 'No'}</span>
                        <span class="metric-status neutral">
                            ${analysis.hasQuotes ? 'Attribution' : 'Direct'}
                        </span>
                    </div>
                </div>
            </div>
        `;
    }

    renderTactics(tactics) {
        if (tactics.length === 0) return '';
        
        return `
            <div class="tactics-section">
                <h5>Manipulation Tactics Detected</h5>
                <div class="tactics-list">
                    ${tactics.map(tactic => `
                        <div class="tactic-item ${tactic.severity}">
                            <div class="tactic-header">
                                <span class="tactic-name">${tactic.name}</span>
                                <span class="severity-badge">${tactic.severity}</span>
                            </div>
                            <p class="tactic-description">${tactic.description}</p>
                            <p class="tactic-example">Example: ${tactic.example}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderExamples(examples) {
        if (examples.length === 0) return '';
        
        return `
            <div class="examples-section">
                <h5>Specific Examples Found</h5>
                <div class="examples-list">
                    ${examples.map(example => `
                        <div class="example-item">
                            <span class="example-type">${example.type}:</span>
                            <span class="example-text">"${example.text}"</span>
                            <p class="example-context">${example.context}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    getReadingTips(score) {
        const tips = [];
        
        if (score > 40) {
            tips.push('Check if the article delivers on the headline\'s promise');
            tips.push('Look for specific facts rather than vague claims');
        }
        
        if (score > 60) {
            tips.push('Be skeptical of extreme claims or emotional language');
            tips.push('Verify shocking statistics with original sources');
        }
        
        if (score > 80) {
            tips.push('Consider finding alternative sources for this story');
            tips.push('Focus on facts, ignore sensational framing');
        }
        
        if (tips.length === 0) {
            tips.push('This appears to be straightforward reporting');
            tips.push('Standard critical reading practices apply');
        }
        
        return tips;
    }

    initializeGauge(score) {
        const canvas = document.getElementById('clickbaitGauge');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        const centerX = width / 2;
        const centerY = height - 20;
        const radius = 100;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw background arc
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI);
        ctx.lineWidth = 20;
        ctx.strokeStyle = '#e5e7eb';
        ctx.stroke();
        
        // Calculate angle for score
        const angle = Math.PI + (score / 100) * Math.PI;
        
        // Draw score arc with gradient
        const gradient = ctx.createLinearGradient(50, 0, 250, 0);
        gradient.addColorStop(0, '#10b981');
        gradient.addColorStop(0.3, '#3b82f6');
        gradient.addColorStop(0.6, '#f59e0b');
        gradient.addColorStop(1, '#ef4444');
        
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, angle);
        ctx.lineWidth = 20;
        ctx.strokeStyle = gradient;
        ctx.stroke();
        
        // Draw pointer
        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(angle - Math.PI / 2);
        
        ctx.beginPath();
        ctx.moveTo(0, -radius + 30);
        ctx.lineTo(-5, -radius + 45);
        ctx.lineTo(5, -radius + 45);
        ctx.closePath();
        ctx.fillStyle = '#1f2937';
        ctx.fill();
        
        ctx.restore();
        
        // Draw center circle
        ctx.beginPath();
        ctx.arc(centerX, centerY, 10, 0, 2 * Math.PI);
        ctx.fillStyle = '#1f2937';
        ctx.fill();
        
        // Draw score text
        ctx.font = 'bold 36px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = '#1f2937';
        ctx.fillText(score, centerX, centerY - 30);
        
        ctx.font = '12px sans-serif';
        ctx.fillStyle = '#6b7280';
        ctx.fillText('CLICKBAIT SCORE', centerX, centerY - 10);
    }

    getClickbaitLevel(score) {
        if (score < 20) return 'Minimal';
        if (score < 40) return 'Low';
        if (score < 60) return 'Moderate';
        if (score < 80) return 'High';
        return 'Extreme';
    }

    extractExample(text, terms) {
        for (const term of terms) {
            if (text.toLowerCase().includes(term.toLowerCase())) {
                return `Uses "${term}"`;
            }
        }
        return 'Pattern detected';
    }
}

// Add styles
const style = document.createElement('style');
style.textContent = `
    .clickbait-detector-container {
        padding: 20px;
    }

    .clickbait-gauge-container {
        text-align: center;
        margin: 20px 0;
        position: relative;
    }

    .gauge-labels {
        display: flex;
        justify-content: space-between;
        padding: 0 20px;
        font-size: 11px;
        color: #6b7280;
        margin-top: -10px;
    }

    .score-breakdown {
        margin: 20px 0;
        text-align: center;
    }

    .recommendation-box {
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
    }

    .recommendation-box.minimal { background: #f0fdf4; border: 1px solid #86efac; }
    .recommendation-box.low { background: #eff6ff; border: 1px solid #93bbfe; }
    .recommendation-box.moderate { background: #fef3c7; border: 1px solid #fcd34d; }
    .recommendation-box.high { background: #fef2e8; border: 1px solid #fdba74; }
    .recommendation-box.extreme { background: #fee2e2; border: 1px solid #fca5a5; }

    .indicators-grid {
        display: grid;
        gap: 15px;
        margin-top: 15px;
    }

    .indicator-card {
        background: #f9fafb;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }

    .indicator-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }

    .indicator-score {
        color: #ef4444;
        font-weight: 600;
    }

    .match-chip {
        display: inline-block;
        background: #dbeafe;
        color: #1e40af;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        margin: 2px;
    }

    .analysis-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
        margin-top: 15px;
    }

    .metric {
        background: #f9fafb;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
    }

    .metric-label {
        display: block;
        font-size: 12px;
        color: #6b7280;
        margin-bottom: 4px;
    }

    .metric-value {
        display: block;
        font-size: 18px;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 4px;
    }

    .metric-status {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 500;
    }

    .metric-status.good { background: #d1fae5; color: #065f46; }
    .metric-status.warning { background: #fef3c7; color: #92400e; }
    .metric-status.neutral { background: #e5e7eb; color: #374151; }

    .tactics-list {
        margin-top: 15px;
    }

    .tactic-item {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }

    .tactic-item.low { background: #f3f4f6; }
    .tactic-item.moderate { background: #fef3c7; }
    .tactic-item.high { background: #fee2e2; }

    .severity-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 500;
        text-transform: uppercase;
    }

    .simple-meter {
        height: 8px;
        background: #e5e7eb;
        border-radius: 4px;
        overflow: hidden;
        margin: 10px 0;
    }

    .meter-fill {
        height: 100%;
        transition: width 0.5s ease;
    }

    .meter-fill.minimal { background: #10b981; }
    .meter-fill.low { background: #3b82f6; }
    .meter-fill.moderate { background: #f59e0b; }
    .meter-fill.high { background: #f97316; }
    .meter-fill.extreme { background: #ef4444; }

    .reader-advisory {
        background: #f9fafb;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }

    .reader-advisory h5 {
        margin-bottom: 10px;
        color: #1f2937;
    }

    .reader-advisory ul {
        margin: 0;
        padding-left: 20px;
    }

    .reader-advisory li {
        margin-bottom: 5px;
        color: #4b5563;
    }
`;
document.head.appendChild(style);

// Register globally
window.ClickbaitDetector = ClickbaitDetector;
