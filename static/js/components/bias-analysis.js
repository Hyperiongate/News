// static/js/components/bias-analysis.js
// Enhanced Bias Analysis Component with Multi-Dimensional Analysis

class BiasAnalysis {
    constructor() {
        this.container = null;
        this.data = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'bias-analysis-container analysis-card';
        
        const biasData = data.bias_analysis || {};
        const isPro = data.is_pro !== false;
        
        this.data = biasData;
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">⚖️</span>
                <span>Bias Analysis</span>
                ${isPro ? '<span class="pro-indicator">PRO</span>' : ''}
            </div>
            
            <div class="bias-content">
                ${isPro ? this.renderProBiasAnalysis(biasData) : this.renderBasicBiasAnalysis(biasData)}
            </div>
        `;
        
        this.container = container;
        
        // Initialize visualizations after render
        setTimeout(() => this.initializeVisualizations(), 100);
        
        return container;
    }

    renderBasicBiasAnalysis(biasData) {
        const politicalLean = biasData.political_lean || 0;
        const overallBias = biasData.overall_bias || 'Unknown';
        
        return `
            <div class="bias-basic">
                <p><strong>Political Bias:</strong> ${overallBias}</p>
                <p><strong>Objectivity Score:</strong> ${biasData.objectivity_score || 'N/A'}%</p>
                <div class="upgrade-prompt">
                    <span class="lock-icon">🔒</span>
                    <p>Unlock comprehensive bias analysis across 5 dimensions with Pro</p>
                </div>
            </div>
        `;
    }

    renderProBiasAnalysis(biasData) {
        return `
            <!-- Enhanced Bias Overview -->
            <div class="bias-overview-section">
                <h4>Multi-Dimensional Bias Detection</h4>
                <p class="bias-explanation">
                    Our AI analyzes bias across 5 key dimensions, examining word choice, framing, 
                    source selection, and narrative structure to provide a comprehensive bias profile.
                </p>
                
                <!-- Overall Bias Summary -->
                <div class="overall-bias-summary">
                    <div class="bias-metric">
                        <span class="metric-label">Overall Bias:</span>
                        <span class="metric-value ${this.getBiasClass(biasData.overall_bias)}">${biasData.overall_bias || 'Unknown'}</span>
                    </div>
                    <div class="bias-metric">
                        <span class="metric-label">Objectivity Score:</span>
                        <span class="metric-value">${biasData.objectivity_score || 0}%</span>
                    </div>
                    <div class="bias-metric">
                        <span class="metric-label">Confidence:</span>
                        <span class="metric-value">${biasData.bias_confidence || 0}%</span>
                    </div>
                </div>
            </div>

            <!-- Political Bias Spectrum -->
            <div class="political-bias-section">
                <h4>Political Bias Spectrum</h4>
                <div class="bias-scale-container">
                    <div class="bias-scale">
                        <div class="bias-gradient"></div>
                        <div class="bias-marker" style="left: ${this.calculateMarkerPosition(biasData.political_lean)}%">
                            <div class="marker-dot"></div>
                            <div class="marker-value">${this.formatBiasScore(biasData.political_lean)}</div>
                        </div>
                        ${biasData.bias_confidence ? `
                            <div class="confidence-band" style="left: ${this.calculateConfidenceBand(biasData).left}%; width: ${this.calculateConfidenceBand(biasData).width}%"></div>
                        ` : ''}
                    </div>
                    <div class="bias-labels">
                        <span>Far Left</span>
                        <span>Left</span>
                        <span>Center</span>
                        <span>Right</span>
                        <span>Far Right</span>
                    </div>
                </div>
                <p class="bias-interpretation">
                    ${this.getBiasInterpretation(biasData.political_lean)}
                </p>
            </div>

            <!-- 5-Dimensional Bias Analysis -->
            <div class="dimensional-bias-section">
                <h4>5-Dimensional Bias Analysis</h4>
                <div class="dimensions-grid">
                    ${this.renderBiasDimensions(biasData.bias_dimensions)}
                </div>
            </div>

            <!-- Bias Patterns Detected -->
            ${biasData.bias_patterns && biasData.bias_patterns.length > 0 ? `
                <div class="bias-patterns-section">
                    <h4>Detected Bias Patterns</h4>
                    <div class="patterns-list">
                        ${biasData.bias_patterns.map(pattern => this.renderBiasPattern(pattern)).join('')}
                    </div>
                </div>
            ` : ''}

            <!-- Loaded Phrases Analysis -->
            ${biasData.loaded_phrases && biasData.loaded_phrases.length > 0 ? `
                <div class="loaded-phrases-section">
                    <h4>Loaded Language Analysis</h4>
                    <p class="section-explanation">
                        These emotionally charged or biased phrases were detected in the article:
                    </p>
                    <div class="phrases-grid">
                        ${biasData.loaded_phrases.map(phrase => this.renderLoadedPhrase(phrase)).join('')}
                    </div>
                </div>
            ` : ''}

            <!-- Framing Analysis -->
            ${biasData.framing_analysis ? `
                <div class="framing-analysis-section">
                    <h4>Framing Analysis</h4>
                    <p class="section-explanation">
                        How the article frames issues can reveal underlying bias:
                    </p>
                    ${this.renderFramingAnalysis(biasData.framing_analysis)}
                </div>
            ` : ''}

            <!-- Manipulation Tactics -->
            ${biasData.manipulation_tactics && biasData.manipulation_tactics.length > 0 ? `
                <div class="manipulation-section">
                    <h4>Manipulation Tactics Detected</h4>
                    <div class="tactics-grid">
                        ${biasData.manipulation_tactics.map(tactic => this.renderManipulationTactic(tactic)).join('')}
                    </div>
                </div>
            ` : ''}

            <!-- Comparative Context -->
            ${biasData.comparative_context ? `
                <div class="comparative-context-section">
                    <h4>Industry Comparison</h4>
                    <p>${biasData.comparative_context.description || 'This level of bias is typical for this type of content.'}</p>
                    ${biasData.comparative_context.similar_sources ? `
                        <p class="similar-sources">
                            <strong>Similar bias level found in:</strong> ${biasData.comparative_context.similar_sources.join(', ')}
                        </p>
                    ` : ''}
                </div>
            ` : ''}
        `;
    }

    renderBiasDimensions(dimensions) {
        if (!dimensions) {
            return '<p>No dimensional analysis available</p>';
        }

        const dimensionInfo = {
            political: {
                icon: '🏛️',
                description: 'Left-Right political spectrum',
                labels: ['Far Left', 'Center', 'Far Right']
            },
            corporate: {
                icon: '🏢',
                description: 'Corporate vs. Anti-corporate stance',
                labels: ['Anti-Corp', 'Neutral', 'Pro-Corp']
            },
            sensational: {
                icon: '📰',
                description: 'Factual vs. Sensationalized reporting',
                labels: ['Factual', 'Balanced', 'Sensational']
            },
            nationalistic: {
                icon: '🌍',
                description: 'Nationalistic vs. Internationalist perspective',
                labels: ['Internationalist', 'Balanced', 'Nationalist']
            },
            establishment: {
                icon: '🏛️',
                description: 'Establishment vs. Anti-establishment view',
                labels: ['Anti-Establishment', 'Neutral', 'Pro-Establishment']
            }
        };

        return Object.entries(dimensions).map(([key, dim]) => {
            const info = dimensionInfo[key] || { icon: '📊', description: key, labels: ['Low', 'Medium', 'High'] };
            const score = dim.score * 100; // Convert to percentage
            
            return `
                <div class="dimension-card">
                    <div class="dimension-header">
                        <span class="dimension-icon">${info.icon}</span>
                        <span class="dimension-name">${key.charAt(0).toUpperCase() + key.slice(1)}</span>
                    </div>
                    <p class="dimension-description">${info.description}</p>
                    <div class="dimension-scale">
                        <div class="scale-bar">
                            <div class="scale-fill" style="width: ${Math.abs(score)}%; background: ${this.getDimensionColor(score)}"></div>
                            <div class="scale-marker" style="left: 50%"></div>
                        </div>
                        <div class="scale-labels">
                            <span>${info.labels[0]}</span>
                            <span>${info.labels[1]}</span>
                            <span>${info.labels[2]}</span>
                        </div>
                    </div>
                    <p class="dimension-score">
                        Score: ${dim.score.toFixed(2)} (${dim.label || this.getDimensionLabel(score)})
                    </p>
                </div>
            `;
        }).join('');
    }

    renderBiasPattern(pattern) {
        const patternDescriptions = {
            'cherry-picking': 'Selective use of facts to support a predetermined conclusion',
            'strawman': 'Misrepresenting opposing views to make them easier to attack',
            'false-balance': 'Presenting fringe views as equally valid to mainstream consensus',
            'loaded-questions': 'Questions that contain controversial assumptions',
            'anecdotal': 'Using personal stories as evidence for broad claims'
        };

        return `
            <div class="pattern-card">
                <div class="pattern-header">
                    <span class="pattern-icon">🔍</span>
                    <span class="pattern-name">${pattern.name || pattern}</span>
                </div>
                <p class="pattern-description">
                    ${patternDescriptions[pattern.type || pattern] || pattern.description || 'Bias pattern detected in content'}
                </p>
                ${pattern.examples && pattern.examples.length > 0 ? `
                    <div class="pattern-examples">
                        <strong>Examples found:</strong>
                        <ul>
                            ${pattern.examples.map(ex => `<li>"${ex}"</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                ${pattern.severity ? `
                    <div class="pattern-severity severity-${pattern.severity.toLowerCase()}">
                        Severity: ${pattern.severity}
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderLoadedPhrase(phrase) {
        const phraseObj = typeof phrase === 'string' ? { text: phrase } : phrase;
        
        return `
            <div class="loaded-phrase-card">
                <div class="phrase-text">"${phraseObj.text || phraseObj}"</div>
                ${phraseObj.context ? `
                    <div class="phrase-context">
                        <strong>Context:</strong> ${phraseObj.context}
                    </div>
                ` : ''}
                ${phraseObj.bias_type ? `
                    <div class="phrase-type">
                        Type: ${phraseObj.bias_type}
                    </div>
                ` : ''}
                ${phraseObj.alternative ? `
                    <div class="phrase-alternative">
                        <strong>Neutral alternative:</strong> "${phraseObj.alternative}"
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderFramingAnalysis(framing) {
        const framingTypes = {
            victim: { icon: '😢', description: 'Presents subjects as victims' },
            hero: { icon: '🦸', description: 'Presents subjects as heroes' },
            threat: { icon: '⚠️', description: 'Frames issues as threats' },
            progress: { icon: '📈', description: 'Frames as progress/achievement' }
        };

        return `
            <div class="framing-grid">
                ${Object.entries(framing).map(([type, data]) => {
                    const info = framingTypes[type] || { icon: '📋', description: type };
                    
                    return `
                        <div class="framing-card ${data.detected ? 'detected' : ''}">
                            <div class="framing-icon">${info.icon}</div>
                            <div class="framing-type">${type.charAt(0).toUpperCase() + type.slice(1)} Framing</div>
                            <div class="framing-description">${info.description}</div>
                            ${data.detected ? `
                                <div class="framing-score">
                                    Strength: ${(data.score * 100).toFixed(0)}%
                                </div>
                                ${data.examples && data.examples.length > 0 ? `
                                    <div class="framing-examples">
                                        ${data.examples.map(ex => `<div class="example">"${ex}"</div>`).join('')}
                                    </div>
                                ` : ''}
                            ` : '<div class="not-detected">Not detected</div>'}
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }

    renderManipulationTactic(tactic) {
        const tacticInfo = {
            'fear-mongering': { icon: '😨', severity: 'high' },
            'emotional-manipulation': { icon: '❤️', severity: 'medium' },
            'false-urgency': { icon: '⏰', severity: 'medium' },
            'loaded-language': { icon: '💭', severity: 'low' }
        };

        const info = tacticInfo[tactic.type] || { icon: '⚠️', severity: 'medium' };
        
        return `
            <div class="tactic-card severity-${tactic.severity || info.severity}">
                <div class="tactic-header">
                    <span class="tactic-icon">${info.icon}</span>
                    <span class="tactic-name">${tactic.name || tactic.type || tactic}</span>
                </div>
                ${tactic.description ? `
                    <p class="tactic-description">${tactic.description}</p>
                ` : ''}
                ${tactic.impact ? `
                    <div class="tactic-impact">
                        <strong>Impact:</strong> ${tactic.impact}
                    </div>
                ` : ''}
                ${tactic.count ? `
                    <div class="tactic-count">
                        Found ${tactic.count} instance${tactic.count > 1 ? 's' : ''}
                    </div>
                ` : ''}
            </div>
        `;
    }

    calculateMarkerPosition(politicalLean) {
        // Convert from -100 to 100 scale to 0 to 100 for positioning
        return ((politicalLean + 100) / 200) * 100;
    }

    calculateConfidenceBand(biasData) {
        const confidence = biasData.bias_confidence || 80;
        const uncertainty = (100 - confidence) / 100;
        const position = this.calculateMarkerPosition(biasData.political_lean);
        const bandWidth = uncertainty * 30; // Max 30% width for low confidence
        
        return {
            left: Math.max(0, position - bandWidth / 2),
            width: Math.min(100, bandWidth)
        };
    }

    formatBiasScore(score) {
        if (score > 0) return `+${score}`;
        return score.toString();
    }

    getBiasInterpretation(politicalLean) {
        const absLean = Math.abs(politicalLean);
        const direction = politicalLean < 0 ? 'left' : 'right';
        
        if (absLean < 10) {
            return 'This article demonstrates relatively balanced political coverage with minimal partisan bias.';
        } else if (absLean < 30) {
            return `This article shows a slight ${direction}-leaning perspective, which is common in mainstream media.`;
        } else if (absLean < 60) {
            return `This article exhibits moderate ${direction}-wing bias. Critical evaluation of claims is recommended.`;
        } else {
            return `This article shows strong ${direction}-wing bias. Consider seeking alternative perspectives for balance.`;
        }
    }

    getDimensionColor(score) {
        const absScore = Math.abs(score);
        if (absScore < 30) return '#10b981';
        if (absScore < 60) return '#f59e0b';
        return '#ef4444';
    }

    getDimensionLabel(score) {
        const absScore = Math.abs(score);
        if (absScore < 30) return 'Balanced';
        if (absScore < 60) return 'Moderate';
        return 'Strong';
    }

    getBiasClass(bias) {
        if (!bias) return '';
        const lower = bias.toLowerCase();
        if (lower.includes('minimal') || lower.includes('balanced')) return 'bias-minimal';
        if (lower.includes('slight') || lower.includes('moderate')) return 'bias-moderate';
        if (lower.includes('strong') || lower.includes('heavy')) return 'bias-strong';
        return '';
    }

    initializeVisualizations() {
        // Animate dimension scales
        const scales = this.container.querySelectorAll('.scale-fill');
        scales.forEach(scale => {
            const width = scale.style.width;
            scale.style.width = '0';
            setTimeout(() => {
                scale.style.transition = 'width 1s ease-out';
                scale.style.width = width;
            }, 100);
        });

        // Add hover effects
        const cards = this.container.querySelectorAll('.dimension-card, .pattern-card, .loaded-phrase-card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-2px)';
                card.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
                card.style.boxShadow = 'none';
            });
        });
    }
}

// Export and register
window.BiasAnalysis = BiasAnalysis;

// Auto-register with UI controller
document.addEventListener('DOMContentLoaded', () => {
    if (window.UI) {
        window.UI.registerComponent('biasAnalysis', new BiasAnalysis());
    }
});
