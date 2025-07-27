// static/js/components/trust-score.js
// Enhanced Trust Score Component with detailed breakdowns and insights

class TrustScore {
    constructor() {
        this.score = 0;
        this.data = null;
    }

    render(score, data) {
        this.score = score || 0;
        this.data = data;
        
        const container = document.createElement('div');
        container.className = 'trust-score-container';
        
        // Determine score category
        const category = this.getScoreCategory(this.score);
        
        // Calculate detailed breakdowns
        const breakdown = this.calculateDetailedBreakdown(data);
        const insights = this.generateInsights(breakdown, data);
        
        container.innerHTML = `
            <div class="trust-score-card ${category.class}">
                <div class="trust-score-header">
                    <h3>Comprehensive Trust Analysis</h3>
                    <span class="trust-badge">${category.label}</span>
                </div>
                
                <div class="trust-score-visual">
                    <div class="score-circle-section">
                        <div class="score-circle">
                            <svg viewBox="0 0 200 200" class="score-svg">
                                <!-- Background circle -->
                                <circle cx="100" cy="100" r="90" fill="none" stroke="#e5e7eb" stroke-width="12"/>
                                <!-- Progress circle -->
                                <circle cx="100" cy="100" r="90" fill="none" 
                                    stroke="${category.color}" 
                                    stroke-width="12"
                                    stroke-linecap="round"
                                    stroke-dasharray="${this.getCircumference()}"
                                    stroke-dashoffset="${this.getCircumference()}"
                                    transform="rotate(-90 100 100)"
                                    class="score-progress"/>
                            </svg>
                            <div class="score-text">
                                <span class="score-number">${this.score}</span>
                                <span class="score-label">Trust Score</span>
                            </div>
                        </div>
                        <div class="score-range-indicator">
                            ${this.renderScoreRange(this.score)}
                        </div>
                    </div>
                    
                    <div class="score-breakdown-section">
                        ${this.renderDetailedBreakdown(breakdown)}
                    </div>
                </div>
                
                <div class="trust-insights">
                    <h4>Key Trust Indicators</h4>
                    ${this.renderInsights(insights)}
                </div>
                
                <div class="trust-interpretation">
                    <h4>What This Score Means</h4>
                    <p class="interpretation-text">${category.interpretation}</p>
                    ${this.renderDetailedRecommendations(category, insights)}
                </div>
                
                <div class="trust-components">
                    <h4>Score Components Analysis</h4>
                    ${this.renderComponentsChart(breakdown)}
                </div>
                
                <div class="credibility-signals">
                    <h4>Credibility Signals Found</h4>
                    ${this.renderCredibilitySignals(data)}
                </div>
                
                ${this.renderComparativeContext(this.score)}
            </div>
        `;
        
        // Animate the score circle after rendering
        setTimeout(() => {
            const circle = container.querySelector('.score-progress');
            if (circle) {
                circle.style.transition = 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
                circle.style.strokeDashoffset = this.getOffset();
            }
            
            // Animate component bars
            container.querySelectorAll('.component-bar-fill').forEach((bar, index) => {
                setTimeout(() => {
                    bar.style.width = bar.dataset.width;
                }, 100 + (index * 50));
            });
        }, 100);
        
        return container;
    }

    calculateDetailedBreakdown(data) {
        const breakdown = {
            sourceCredibility: {
                label: 'Source Credibility',
                weight: 30,
                score: 0,
                details: []
            },
            authorCredibility: {
                label: 'Author Credibility',
                weight: 20,
                score: 0,
                details: []
            },
            contentObjectivity: {
                label: 'Content Objectivity',
                weight: 15,
                score: 0,
                details: []
            },
            transparency: {
                label: 'Transparency',
                weight: 15,
                score: 0,
                details: []
            },
            factualAccuracy: {
                label: 'Factual Accuracy',
                weight: 10,
                score: 0,
                details: []
            },
            manipulationRisk: {
                label: 'Manipulation Risk',
                weight: 10,
                score: 0,
                details: []
            }
        };
        
        // Calculate Source Credibility
        if (data?.source_credibility) {
            const rating = data.source_credibility.rating;
            breakdown.sourceCredibility.score = {
                'High': 90,
                'Medium': 60,
                'Low': 30,
                'Very Low': 10,
                'Unknown': 50
            }[rating] || 50;
            
            breakdown.sourceCredibility.details.push({
                text: `${data.article?.domain || 'Source'} rated as ${rating}`,
                positive: rating === 'High' || rating === 'Medium'
            });
            
            if (data.source_credibility.bias) {
                breakdown.sourceCredibility.details.push({
                    text: `Known ${data.source_credibility.bias} bias`,
                    positive: false
                });
            }
        }
        
        // Calculate Author Credibility
        if (data?.author_analysis) {
            const authorScore = data.author_analysis.credibility_score || 50;
            breakdown.authorCredibility.score = authorScore;
            
            if (data.author_analysis.found) {
                breakdown.authorCredibility.details.push({
                    text: `Author verified: ${data.author_analysis.name}`,
                    positive: true
                });
                
                if (data.author_analysis.years_experience) {
                    breakdown.authorCredibility.details.push({
                        text: `${data.author_analysis.years_experience} years experience`,
                        positive: data.author_analysis.years_experience > 5
                    });
                }
            } else {
                breakdown.authorCredibility.details.push({
                    text: 'Author not verified',
                    positive: false
                });
            }
        }
        
        // Calculate Content Objectivity
        if (data?.bias_analysis) {
            const objectivity = data.bias_analysis.objectivity_score || 0.5;
            breakdown.contentObjectivity.score = Math.round(objectivity * 100);
            
            if (data.bias_analysis.political_lean) {
                const lean = Math.abs(data.bias_analysis.political_lean);
                breakdown.contentObjectivity.details.push({
                    text: lean > 50 ? 'Strong political bias detected' : 'Moderate political perspective',
                    positive: lean <= 50
                });
            }
            
            if (data.bias_analysis.manipulation_tactics?.length > 0) {
                breakdown.contentObjectivity.details.push({
                    text: `${data.bias_analysis.manipulation_tactics.length} manipulation tactics found`,
                    positive: false
                });
            }
        }
        
        // Calculate Transparency
        if (data?.transparency_analysis) {
            breakdown.transparency.score = data.transparency_analysis.transparency_score || 50;
            
            const hasAuthor = data.article?.author && data.article.author !== 'Unknown Author';
            breakdown.transparency.details.push({
                text: hasAuthor ? 'Author clearly identified' : 'No author attribution',
                positive: hasAuthor
            });
            
            if (data.transparency_analysis.sources_cited) {
                breakdown.transparency.details.push({
                    text: `${data.transparency_analysis.sources_cited} sources cited`,
                    positive: data.transparency_analysis.sources_cited > 2
                });
            }
        }
        
        // Calculate Factual Accuracy
        if (data?.fact_checks && data.fact_checks.length > 0) {
            const verified = data.fact_checks.filter(fc => 
                fc.verdict && fc.verdict.toLowerCase().includes('true')
            ).length;
            const accuracy = Math.round((verified / data.fact_checks.length) * 100);
            breakdown.factualAccuracy.score = accuracy;
            
            breakdown.factualAccuracy.details.push({
                text: `${verified}/${data.fact_checks.length} claims verified as true`,
                positive: accuracy >= 70
            });
            
            const highConfidence = data.fact_checks.filter(fc => fc.confidence >= 70).length;
            if (highConfidence > 0) {
                breakdown.factualAccuracy.details.push({
                    text: `${highConfidence} high-confidence verifications`,
                    positive: true
                });
            }
        } else {
            breakdown.factualAccuracy.score = 50; // Neutral if no fact checks
        }
        
        // Calculate Manipulation Risk
        const clickbaitScore = data?.clickbait_score || 0;
        const manipulationScore = data?.persuasion_analysis?.persuasion_score || 0;
        breakdown.manipulationRisk.score = 100 - Math.max(clickbaitScore, manipulationScore);
        
        if (clickbaitScore > 60) {
            breakdown.manipulationRisk.details.push({
                text: 'High clickbait indicators',
                positive: false
            });
        }
        
        if (manipulationScore > 60) {
            breakdown.manipulationRisk.details.push({
                text: 'Emotional manipulation detected',
                positive: false
            });
        }
        
        return breakdown;
    }

    generateInsights(breakdown, data) {
        const insights = {
            strengths: [],
            concerns: [],
            dataQuality: []
        };
        
        // Analyze strengths
        Object.entries(breakdown).forEach(([key, component]) => {
            if (component.score >= 80) {
                insights.strengths.push({
                    icon: this.getComponentIcon(key),
                    text: `Strong ${component.label.toLowerCase()}`
                });
            }
        });
        
        // Analyze concerns
        Object.entries(breakdown).forEach(([key, component]) => {
            if (component.score < 40) {
                insights.concerns.push({
                    icon: this.getComponentIcon(key),
                    text: `Weak ${component.label.toLowerCase()}`
                });
            }
        });
        
        // Data quality insights
        if (data?.key_claims && data.key_claims.length > 5) {
            insights.dataQuality.push({
                icon: '📊',
                text: 'Rich in factual claims'
            });
        }
        
        if (data?.fact_checks && data.fact_checks.length > 0) {
            insights.dataQuality.push({
                icon: '✓',
                text: `${data.fact_checks.length} claims fact-checked`
            });
        }
        
        if (data?.related_articles && data.related_articles.length > 0) {
            insights.dataQuality.push({
                icon: '📰',
                text: 'Cross-referenced with other sources'
            });
        }
        
        return insights;
    }

    renderDetailedBreakdown(breakdown) {
        return `
            <div class="breakdown-components">
                ${Object.entries(breakdown).map(([key, component]) => `
                    <div class="component-item">
                        <div class="component-header">
                            <span class="component-name">${component.label}</span>
                            <span class="component-score">${component.score}/100</span>
                        </div>
                        <div class="component-bar">
                            <div class="component-bar-fill ${this.getScoreClass(component.score)}" 
                                 data-width="${component.score}%" 
                                 style="width: 0%"></div>
                        </div>
                        <div class="component-weight">Weight: ${component.weight}%</div>
                        ${component.details.length > 0 ? `
                            <div class="component-details">
                                ${component.details.map(detail => `
                                    <div class="detail-item ${detail.positive ? 'positive' : 'negative'}">
                                        <span class="detail-icon">${detail.positive ? '✓' : '⚠'}</span>
                                        <span class="detail-text">${detail.text}</span>
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderInsights(insights) {
        return `
            <div class="insights-grid">
                ${insights.strengths.length > 0 ? `
                    <div class="insight-section strengths">
                        <h5>✅ Strengths</h5>
                        ${insights.strengths.map(item => `
                            <div class="insight-item">
                                <span class="insight-icon">${item.icon}</span>
                                <span>${item.text}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${insights.concerns.length > 0 ? `
                    <div class="insight-section concerns">
                        <h5>⚠️ Concerns</h5>
                        ${insights.concerns.map(item => `
                            <div class="insight-item">
                                <span class="insight-icon">${item.icon}</span>
                                <span>${item.text}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${insights.dataQuality.length > 0 ? `
                    <div class="insight-section data-quality">
                        <h5>📊 Analysis Quality</h5>
                        ${insights.dataQuality.map(item => `
                            <div class="insight-item">
                                <span class="insight-icon">${item.icon}</span>
                                <span>${item.text}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderDetailedRecommendations(category, insights) {
        const recommendations = [];
        
        // Base recommendation
        recommendations.push({
            priority: 'primary',
            icon: '💡',
            text: category.recommendation
        });
        
        // Specific recommendations based on insights
        if (insights.concerns.some(c => c.text.includes('author'))) {
            recommendations.push({
                priority: 'high',
                icon: '🔍',
                text: 'Verify author credentials independently'
            });
        }
        
        if (insights.concerns.some(c => c.text.includes('fact'))) {
            recommendations.push({
                priority: 'high',
                icon: '📋',
                text: 'Cross-check factual claims with primary sources'
            });
        }
        
        if (this.score < 60) {
            recommendations.push({
                priority: 'critical',
                icon: '⚠️',
                text: 'Consider finding alternative sources for this information'
            });
        }
        
        return `
            <div class="recommendations-list">
                ${recommendations.map(rec => `
                    <div class="recommendation-item ${rec.priority}">
                        <span class="recommendation-icon">${rec.icon}</span>
                        <span class="recommendation-text">${rec.text}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderComponentsChart(breakdown) {
        // Calculate maximum possible score vs actual score
        const components = Object.entries(breakdown).map(([key, component]) => ({
            name: component.label,
            actual: (component.score * component.weight) / 100,
            possible: component.weight,
            percentage: component.score
        }));
        
        return `
            <div class="components-chart">
                <div class="chart-header">
                    <span>Component</span>
                    <span>Contribution to Score</span>
                </div>
                ${components.map(comp => `
                    <div class="chart-row">
                        <span class="component-label">${comp.name}</span>
                        <div class="contribution-visual">
                            <div class="contribution-bar">
                                <div class="contribution-possible" style="width: ${comp.possible}%">
                                    <div class="contribution-actual ${this.getScoreClass(comp.percentage)}" 
                                         style="width: ${(comp.actual / comp.possible) * 100}%">
                                        <span class="contribution-value">${comp.actual.toFixed(1)}</span>
                                    </div>
                                </div>
                            </div>
                            <span class="contribution-max">/${comp.possible}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderCredibilitySignals(data) {
        const signals = {
            positive: [],
            negative: [],
            neutral: []
        };
        
        // Check for positive signals
        if (data?.source_credibility?.rating === 'High') {
            signals.positive.push('Published by highly credible source');
        }
        
        if (data?.author_analysis?.verification_status?.journalist_verified) {
            signals.positive.push('Author is a verified journalist');
        }
        
        if (data?.fact_checks?.some(fc => fc.publisher && fc.confidence > 80)) {
            signals.positive.push('Claims verified by reputable fact-checkers');
        }
        
        if (data?.transparency_analysis?.sources_cited > 5) {
            signals.positive.push('Multiple sources properly cited');
        }
        
        // Check for negative signals
        if (data?.clickbait_score > 70) {
            signals.negative.push('Sensationalized headline detected');
        }
        
        if (data?.bias_analysis?.manipulation_tactics?.includes('fear_mongering')) {
            signals.negative.push('Fear-based manipulation tactics used');
        }
        
        if (data?.fact_checks?.filter(fc => fc.verdict === 'false').length > 2) {
            signals.negative.push('Multiple false claims identified');
        }
        
        // Neutral observations
        if (data?.article?.publish_date) {
            const daysOld = Math.floor((new Date() - new Date(data.article.publish_date)) / (1000 * 60 * 60 * 24));
            if (daysOld > 365) {
                signals.neutral.push(`Article is ${Math.floor(daysOld / 365)} year(s) old`);
            }
        }
        
        return `
            <div class="credibility-signals-grid">
                ${signals.positive.length > 0 ? `
                    <div class="signals-group positive">
                        <h5>✅ Positive Signals</h5>
                        ${signals.positive.map(signal => `
                            <div class="signal-item">
                                <span class="signal-indicator"></span>
                                <span>${signal}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${signals.negative.length > 0 ? `
                    <div class="signals-group negative">
                        <h5>🚩 Red Flags</h5>
                        ${signals.negative.map(signal => `
                            <div class="signal-item">
                                <span class="signal-indicator"></span>
                                <span>${signal}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${signals.neutral.length > 0 ? `
                    <div class="signals-group neutral">
                        <h5>ℹ️ Additional Context</h5>
                        ${signals.neutral.map(signal => `
                            <div class="signal-item">
                                <span class="signal-indicator"></span>
                                <span>${signal}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderComparativeContext(score) {
        return `
            <div class="comparative-context">
                <h4>How This Compares</h4>
                <div class="comparison-visual">
                    <div class="comparison-scale">
                        <div class="scale-labels">
                            <span>0</span>
                            <span>25</span>
                            <span>50</span>
                            <span>75</span>
                            <span>100</span>
                        </div>
                        <div class="scale-bar">
                            <div class="scale-ranges">
                                <div class="range poor" style="width: 40%"></div>
                                <div class="range fair" style="width: 20%"></div>
                                <div class="range good" style="width: 20%"></div>
                                <div class="range excellent" style="width: 20%"></div>
                            </div>
                            <div class="score-marker" style="left: ${score}%">
                                <span class="marker-label">This Article</span>
                            </div>
                        </div>
                    </div>
                    <div class="comparison-insights">
                        <p>${this.getComparativeInsight(score)}</p>
                    </div>
                </div>
            </div>
        `;
    }

    renderScoreRange(score) {
        const ranges = [
            { min: 0, max: 39, label: 'Poor' },
            { min: 40, max: 59, label: 'Fair' },
            { min: 60, max: 79, label: 'Good' },
            { min: 80, max: 100, label: 'Excellent' }
        ];
        
        return `
            <div class="score-ranges">
                ${ranges.map(range => `
                    <div class="range-item ${score >= range.min && score <= range.max ? 'active' : ''}">
                        <span class="range-label">${range.label}</span>
                        <span class="range-values">${range.min}-${range.max}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    getScoreCategory(score) {
        if (score >= 80) {
            return {
                class: 'excellent',
                label: 'Highly Trustworthy',
                color: '#10b981',
                interpretation: 'This article demonstrates exceptional journalistic standards with verified sources, minimal bias, and strong factual accuracy. The information presented is well-supported and transparent.',
                recommendation: 'This source meets the highest standards of credibility and can be confidently used for research, citation, and sharing.'
            };
        } else if (score >= 60) {
            return {
                class: 'good',
                label: 'Generally Reliable',
                color: '#3b82f6',
                interpretation: 'This article shows good journalistic practices with mostly reliable information. Some minor issues exist but don\'t significantly compromise the overall credibility.',
                recommendation: 'Suitable for general information gathering. For academic or professional use, verify key claims with additional sources.'
            };
        } else if (score >= 40) {
            return {
                class: 'fair',
                label: 'Mixed Reliability',
                color: '#f59e0b',
                interpretation: 'This article contains both reliable and questionable elements. Notable concerns include bias, unverified claims, or credibility issues that require careful evaluation.',
                recommendation: 'Read critically and cross-reference important information. Be aware of potential bias and verify facts independently.'
            };
        } else {
            return {
                class: 'poor',
                label: 'Low Credibility',
                color: '#ef4444',
                interpretation: 'Significant credibility issues detected including potential misinformation, heavy bias, manipulation tactics, or unverifiable sources. The article fails to meet basic journalistic standards.',
                recommendation: 'Not recommended as a reliable source. Seek alternative, more credible sources for this topic.'
            };
        }
    }

    getComponentIcon(key) {
        const icons = {
            sourceCredibility: '🏢',
            authorCredibility: '✍️',
            contentObjectivity: '⚖️',
            transparency: '🔍',
            factualAccuracy: '✓',
            manipulationRisk: '🛡️'
        };
        return icons[key] || '📊';
    }

    getScoreClass(score) {
        if (score >= 80) return 'excellent';
        if (score >= 60) return 'good';
        if (score >= 40) return 'fair';
        return 'poor';
    }

    getComparativeInsight(score) {
        if (score >= 80) {
            return 'This article scores in the top tier of credibility, comparable to established news organizations with strong editorial standards.';
        } else if (score >= 60) {
            return 'This article\'s credibility is above average, similar to mainstream news sources with generally reliable reporting.';
        } else if (score >= 40) {
            return 'This article\'s credibility is below average. Many partisan blogs and opinion sites score in this range.';
        } else {
            return 'This article scores poorly on credibility metrics, similar to sites known for spreading misinformation or extreme bias.';
        }
    }

    getCircumference() {
        return 2 * Math.PI * 90;
    }

    getOffset() {
        const circumference = this.getCircumference();
        return circumference - (this.score / 100) * circumference;
    }
}

// Create and register
window.TrustScore = TrustScore;

document.addEventListener('DOMContentLoaded', () => {
    if (window.UI) {
        window.UI.registerComponent('trustScore', new TrustScore());
    }
});
