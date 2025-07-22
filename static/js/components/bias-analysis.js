// static/js/components/bias-analysis.js

class BiasAnalysis {
    constructor() {
        this.container = null;
        this.chartInstance = null;
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
        
        // Animate and initialize visualizations
        setTimeout(() => {
            this.animateBiasIndicator();
            if (!isBasicPlan && bias.bias_dimensions) {
                this.renderBiasRadarChart(bias.bias_dimensions);
            }
        }, 100);
        
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
        const biasConfidence = bias.bias_confidence || 50;
        const biasDimensions = bias.bias_dimensions || {};
        const biasPatterns = bias.bias_patterns || [];
        const framingAnalysis = bias.framing_analysis || {};
        const biasImpact = bias.bias_impact || {};
        const biasVisualization = bias.bias_visualization || {};
        
        return `
            <div class="analysis-header">
                <span class="analysis-icon">⚖️</span>
                <span>Comprehensive Bias Analysis</span>
                <span class="pro-indicator">PRO</span>
            </div>
            
            <div class="bias-content">
                <!-- Bias Confidence Score -->
                <div class="bias-confidence-section">
                    <div class="confidence-header">
                        <h4>Analysis Confidence</h4>
                        <span class="confidence-value">${biasConfidence}%</span>
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${biasConfidence}%"></div>
                    </div>
                    <p class="confidence-description">
                        ${this.getConfidenceDescription(biasConfidence)}
                    </p>
                </div>

                <!-- Multi-dimensional Bias Analysis -->
                ${Object.keys(biasDimensions).length > 0 ? `
                <div class="multi-dimensional-bias">
                    <h4>Multi-dimensional Bias Analysis</h4>
                    <div class="bias-dimensions-grid">
                        <div class="radar-chart-container">
                            <canvas id="biasRadarChart" width="300" height="300"></canvas>
                        </div>
                        <div class="dimension-details">
                            ${this.renderDimensionDetails(biasDimensions)}
                        </div>
                    </div>
                </div>
                ` : ''}

                <!-- Political Bias Scale (Enhanced) -->
                <div class="political-bias-section">
                    <h4>Political Lean</h4>
                    <div class="bias-scale-container">
                        <div class="bias-scale">
                            <div class="bias-scale-track"></div>
                            <div class="bias-scale-center"></div>
                            ${biasVisualization.confidence_bands ? `
                                <div class="confidence-band" style="left: ${this.calculateIndicatorPosition(biasVisualization.confidence_bands.lower * 100)}%; width: ${(biasVisualization.confidence_bands.upper - biasVisualization.confidence_bands.lower) * 50}%"></div>
                            ` : ''}
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

                <!-- Bias Patterns Detected -->
                ${biasPatterns.length > 0 ? `
                <div class="bias-patterns-section">
                    <h4>🔍 Bias Patterns Detected</h4>
                    <div class="patterns-grid">
                        ${biasPatterns.map(pattern => `
                            <div class="pattern-card severity-${pattern.severity}">
                                <div class="pattern-header">
                                    <span class="pattern-type">${this.formatPatternType(pattern.type)}</span>
                                    <span class="pattern-severity">${pattern.severity}</span>
                                </div>
                                <p class="pattern-description">${pattern.description}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}

                <!-- Framing Analysis -->
                ${framingAnalysis.frames_detected > 0 ? `
                <div class="framing-analysis-section">
                    <h4>🖼️ Framing Analysis</h4>
                    <div class="framing-summary">
                        <p>Article uses <strong>${framingAnalysis.frames_detected}</strong> framing patterns (${framingAnalysis.framing_bias_level} bias level)</p>
                    </div>
                    <div class="framing-patterns">
                        ${this.renderFramingPatterns(framingAnalysis.framing_patterns)}
                    </div>
                </div>
                ` : ''}

                <!-- Bias Impact Assessment -->
                ${biasImpact.severity ? `
                <div class="bias-impact-section">
                    <h4>⚡ Bias Impact Assessment</h4>
                    <div class="impact-severity severity-${biasImpact.severity}">
                        <span>Impact Severity: ${biasImpact.severity.toUpperCase()}</span>
                    </div>
                    <div class="impact-details">
                        <div class="reader-impact">
                            <h5>Potential Reader Impact:</h5>
                            <ul>
                                ${(biasImpact.reader_impact || []).map(impact => `<li>${impact}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="factual-accuracy">
                            <h5>Factual Accuracy:</h5>
                            <p>${biasImpact.factual_accuracy || 'Not assessed'}</p>
                        </div>
                        <div class="recommendation">
                            <h5>Recommendation:</h5>
                            <p class="recommendation-text">${biasImpact.recommendation || 'Read critically'}</p>
                        </div>
                    </div>
                </div>
                ` : ''}

                <!-- Source Selection Bias -->
                ${bias.source_bias_analysis ? `
                <div class="source-bias-section">
                    <h4>📰 Source Selection Analysis</h4>
                    <div class="source-metrics">
                        <div class="metric-item">
                            <span class="metric-label">Total Sources:</span>
                            <span class="metric-value">${bias.source_bias_analysis.total_sources || 0}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Source Diversity:</span>
                            <div class="diversity-score">
                                <div class="diversity-bar">
                                    <div class="diversity-fill" style="width: ${bias.source_bias_analysis.diversity_score || 0}%"></div>
                                </div>
                                <span>${bias.source_bias_analysis.diversity_score || 0}%</span>
                            </div>
                        </div>
                    </div>
                    ${this.renderSourceTypes(bias.source_bias_analysis.source_types)}
                </div>
                ` : ''}

                <!-- Bias Metrics (Original) -->
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
                            <div class="tactic-item severity-${tactic.severity || 'medium'}">
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

                <!-- Enhanced Loaded Language Examples -->
                ${bias.loaded_phrases && bias.loaded_phrases.length > 0 ? `
                <div class="loaded-language-section">
                    <h4>🔥 Loaded Language Analysis</h4>
                    <div class="loaded-phrases-enhanced">
                        ${bias.loaded_phrases.map(phrase => `
                            <div class="loaded-phrase-card">
                                <div class="phrase-header">
                                    <span class="phrase-text">"${phrase.text}"</span>
                                    <span class="phrase-severity severity-${phrase.severity || 'medium'}">${phrase.severity || 'medium'}</span>
                                </div>
                                <div class="phrase-details">
                                    <span class="phrase-type">${phrase.type}</span>
                                    ${phrase.impact ? `<span class="phrase-impact">Impact: ${phrase.impact}</span>` : ''}
                                </div>
                                ${phrase.context ? `<div class="phrase-context">${phrase.context}</div>` : ''}
                                ${phrase.explanation ? `<div class="phrase-explanation">${phrase.explanation}</div>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}

                <!-- Contributing Factors -->
                ${biasVisualization.contributing_factors && biasVisualization.contributing_factors.length > 0 ? `
                <div class="contributing-factors-section">
                    <h4>📊 Main Contributing Factors to Bias</h4>
                    <div class="factors-list">
                        ${biasVisualization.contributing_factors.map(factor => `
                            <div class="factor-item">
                                <div class="factor-header">
                                    <span class="factor-name">${factor.factor}</span>
                                    <span class="factor-impact">${Math.round(factor.impact * 100)}%</span>
                                </div>
                                <div class="factor-bar">
                                    <div class="factor-fill" style="width: ${factor.impact * 100}%"></div>
                                </div>
                                <p class="factor-description">${factor.description}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}

                <!-- Comparative Context -->
                ${bias.comparative_context && bias.comparative_context.industry_standard ? `
                <div class="comparative-context-section">
                    <h4>📈 Industry Context</h4>
                    <p class="context-description">${bias.comparative_context.industry_standard}</p>
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

    renderDimensionDetails(dimensions) {
        if (!dimensions || Object.keys(dimensions).length === 0) return '';
        
        return Object.entries(dimensions).map(([key, data]) => `
            <div class="dimension-item">
                <div class="dimension-header">
                    <span class="dimension-name">${this.formatDimensionName(key)}</span>
                    <span class="dimension-confidence">${data.confidence}% confident</span>
                </div>
                <div class="dimension-label">${data.label}</div>
                <div class="dimension-bar">
                    <div class="dimension-fill" style="width: ${Math.abs(data.score) * 100}%; background: ${this.getDimensionColor(key)}"></div>
                </div>
            </div>
        `).join('');
    }

    renderFramingPatterns(patterns) {
        if (!patterns) return '';
        
        return Object.entries(patterns).filter(([_, data]) => data.detected).map(([frame, data]) => `
            <div class="framing-pattern">
                <h5>${this.formatFrameType(frame)}</h5>
                ${data.examples && data.examples.length > 0 ? `
                    <div class="frame-examples">
                        ${data.examples.map(ex => `<p class="frame-example">"${ex}"</p>`).join('')}
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    renderSourceTypes(sourceTypes) {
        if (!sourceTypes) return '';
        
        const total = Object.values(sourceTypes).reduce((sum, count) => sum + count, 0);
        if (total === 0) return '<p class="no-sources">No sources cited in article</p>';
        
        return `
            <div class="source-types-breakdown">
                ${Object.entries(sourceTypes).filter(([_, count]) => count > 0).map(([type, count]) => `
                    <div class="source-type-item">
                        <span class="source-type-name">${this.formatSourceType(type)}</span>
                        <span class="source-type-count">${count}</span>
                        <div class="source-type-bar">
                            <div class="source-type-fill" style="width: ${(count / total) * 100}%"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderBiasRadarChart(dimensions) {
        const canvas = document.getElementById('biasRadarChart');
        if (!canvas || !dimensions) return;
        
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 40;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Get dimension data
        const dimensionKeys = Object.keys(dimensions);
        const values = dimensionKeys.map(key => Math.abs(dimensions[key].score));
        const labels = dimensionKeys.map(key => this.formatDimensionName(key));
        
        // Draw radar chart
        const angleStep = (Math.PI * 2) / dimensionKeys.length;
        
        // Draw grid
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;
        
        // Draw concentric circles
        for (let i = 1; i <= 5; i++) {
            ctx.beginPath();
            const r = (radius / 5) * i;
            for (let j = 0; j < dimensionKeys.length; j++) {
                const angle = j * angleStep - Math.PI / 2;
                const x = centerX + Math.cos(angle) * r;
                const y = centerY + Math.sin(angle) * r;
                if (j === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.closePath();
            ctx.stroke();
        }
        
        // Draw axes
        for (let i = 0; i < dimensionKeys.length; i++) {
            const angle = i * angleStep - Math.PI / 2;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(
                centerX + Math.cos(angle) * radius,
                centerY + Math.sin(angle) * radius
            );
            ctx.stroke();
        }
        
        // Draw data
        ctx.fillStyle = 'rgba(239, 68, 68, 0.2)';
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 2;
        
        ctx.beginPath();
        for (let i = 0; i < values.length; i++) {
            const angle = i * angleStep - Math.PI / 2;
            const value = values[i];
            const r = radius * value;
            const x = centerX + Math.cos(angle) * r;
            const y = centerY + Math.sin(angle) * r;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        
        // Draw labels
        ctx.fillStyle = '#374151';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        for (let i = 0; i < labels.length; i++) {
            const angle = i * angleStep - Math.PI / 2;
            const labelRadius = radius + 25;
            const x = centerX + Math.cos(angle) * labelRadius;
            const y = centerY + Math.sin(angle) * labelRadius;
            
            // Adjust text alignment based on position
            if (Math.abs(x - centerX) < 10) {
                ctx.textAlign = 'center';
            } else if (x > centerX) {
                ctx.textAlign = 'left';
            } else {
                ctx.textAlign = 'right';
            }
            
            ctx.fillText(labels[i], x, y);
        }
    }

    // Helper methods
    calculateBiasScore(bias) {
        const objectivity = bias.objectivity_score || 50;
        const opinionWeight = 100 - (bias.opinion_percentage || 50);
        const emotionalWeight = 100 - (bias.emotional_score || 50);
        
        return Math.round((objectivity + opinionWeight + emotionalWeight) / 3);
    }

    calculateIndicatorPosition(lean) {
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

    getConfidenceDescription(confidence) {
        if (confidence >= 80) return 'High confidence in bias detection based on substantial evidence';
        if (confidence >= 60) return 'Moderate confidence with clear bias indicators present';
        if (confidence >= 40) return 'Limited confidence due to ambiguous language or insufficient content';
        return 'Low confidence - more content needed for accurate assessment';
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
            'formatting_manipulation': '📝',
            'clickbait': '🎣',
            'default': '⚠️'
        };
        return icons[type] || icons.default;
    }

    formatDimensionName(key) {
        const names = {
            'political': 'Political',
            'corporate': 'Corporate',
            'sensational': 'Sensational',
            'nationalistic': 'Nationalistic',
            'establishment': 'Establishment'
        };
        return names[key] || key.charAt(0).toUpperCase() + key.slice(1);
    }

    getDimensionColor(key) {
        const colors = {
            'political': '#3b82f6',
            'corporate': '#10b981',
            'sensational': '#f59e0b',
            'nationalistic': '#8b5cf6',
            'establishment': '#6b7280'
        };
        return colors[key] || '#374151';
    }

    formatPatternType(type) {
        return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    formatFrameType(frame) {
        return frame.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    formatSourceType(type) {
        return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
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
        const metricFills = this.container?.querySelectorAll('.metric-fill, .confidence-fill, .diversity-fill, .dimension-fill, .factor-fill, .source-type-fill');
        metricFills?.forEach((fill, index) => {
            const width = fill.style.width;
            fill.style.width = '0%';
            setTimeout(() => {
                fill.style.transition = 'width 1s ease-out';
                fill.style.width = width;
            }, 100 + (index * 50));
        });
    }
}

// Export and register with UI controller
window.BiasAnalysis = BiasAnalysis;

// Auto-register when UI controller is available
if (window.UI) {
    window.UI.registerComponent('biasAnalysis', new BiasAnalysis());
}
